"""Stores the ast derived symbols in either github or CERN"""
import ast
import glob
import io
import json
import os
import shutil
import tarfile
from functools import partial
from random import shuffle
from tempfile import TemporaryDirectory

import dask.bag as db
import requests
from dask.diagnostics import ProgressBar
from libcflib.preloader import ReapFailure, fetch_upstream, existing
from libcflib.tools import expand_file_and_mkdirs
from tqdm import tqdm

from symbol_exporter.ast_symbol_extractor import SymbolFinder, version
from symbol_exporter.db_access_model import make_json_friendly, WebDB
from symbol_exporter.python_so_extractor import (
    CompiledPythonLib,
    c_symbols_to_datamodel,
    logger,
)
from symbol_exporter.tools import diff
from dask.distributed import Client

ProgressBar().register()


logger.setLevel("ERROR")

# TODO: push this into the web only branches so we don't require the secret to be set
web_interface = WebDB()


def file_path_to_import(file_path: str):
    return file_path.replace(".py", "").replace("/", ".")


def parse_code(code, module_name):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    z = SymbolFinder(module_name)
    z.visit(tree)
    return z.post_process_symbols()


def single_py_file_extraction(python_file, top_dir):
    folder_path = python_file.rpartition(top_dir + "/")[-1]
    import_name = file_path_to_import(folder_path)
    try:
        with open(python_file, "r") as f:
            code = f.read()
        s = parse_code(code, module_name=import_name)
    except SyntaxError:
        with open(python_file, "r", encoding="utf-8-sig") as f:
            code = f.read()
        s = parse_code(code, module_name=import_name)
    except Exception as e:
        print(python_file, repr(e))
        s = {}
    return s


def parse_so(filename):
    return c_symbols_to_datamodel(CompiledPythonLib(filename).find_symbols())


def single_so_file_extraction(so_file):
    try:
        s = parse_so(so_file)
    except Exception as e:
        try:
            print(so_file, repr(e))
        except Exception as e:
            print(f"Couldn't print exception for {so_file}, {e}")
        s = {}
    return s


def get_all_symbol_names(top_dir):
    symbols_dict = {}
    # walk all the files looking for python files
    py_glob_glob = glob.glob(f"{top_dir}/**/*.py", recursive=True)
    for file_name in [k for k in py_glob_glob]:
        sd = single_py_file_extraction(file_name, top_dir)
        symbols_dict.update(sd)

    py_glob_glob = glob.glob(f"{top_dir}/**/*.so", recursive=True)
    for file_name in [k for k in py_glob_glob]:
        sd = single_so_file_extraction(file_name)
        symbols_dict.update(sd)

    return symbols_dict


def harvest_imports(io_like):
    tf = tarfile.open(fileobj=io_like, mode="r:bz2")
    # TODO: push dir allocation into thread?
    with TemporaryDirectory() as f:
        py_members = [
            m
            for m in tf.getmembers()
            if m.name.endswith(".py")
            or (".cpython" in m.name and m.name.endswith(".so"))
        ]
        tf.extractall(path=f, members=py_members)
        symbols = {}
        found_sp = False
        for root, subdirs, files in os.walk(f):
            # only run if we have a site packages file or it is python itself
            # todo pull up list of python versions or pull it from somewhere else
            if root.lower().endswith("site-packages") or (
                any(
                    root.lower().endswith(f"python{k}")
                    for k in ["2.7", "3.5", "3.6", "3.7", "3.8", "3.9"]
                )
                and "site-packages" not in subdirs
            ):
                found_sp = True
                _symbols = get_all_symbol_names(root)
                symbols.update(_symbols)
    tf.close()
    if not found_sp:
        return None

    return {
        "metadata": {
            "data model version": version,
            "top level symbols": set(k.partition(".")[0] for k in symbols),
        },
        "symbols": symbols,
    }


def fetch_artifact(src_url):
    resp = requests.get(src_url, timeout=60 * 2)
    filelike = io.BytesIO(resp.content)
    return filelike


def fetch_and_run(path, pkg, dst, src_url):
    print(dst)
    filelike = fetch_artifact(src_url)
    try:
        harvested_data = harvest_imports(filelike)
        filelike.close()
        with open(
                expand_file_and_mkdirs(os.path.join(path, pkg, dst)), "w"
        ) as fo:
            json.dump(
                harvested_data, fo, indent=1, sort_keys=True, default=make_json_friendly
            )
        del harvested_data
    except Exception as e:
        raise ReapFailure(pkg, src_url, str(e))


def fetch_and_run_web(pkg, dst, src_url):
    print(dst)
    filelike = fetch_artifact(src_url)
    try:
        harvested_data = harvest_imports(filelike)
        filelike.close()
        web_interface.send_to_webserver(harvested_data, pkg, dst)
        del harvested_data
    except Exception as e:
        raise ReapFailure(pkg, src_url, str(e))


# todo pull this from the og list but reorder that list first
sort_arch_ordering = [
    "noarch",
    "linux-64",
    "osx-64",
    "win-64",
    "linux-ppc64le",
    "linux-aarch64",
    "osx-arm64",
]


def reap(
    path,
    known_bad_packages=(),
    number_to_reap=1000,
    single_thread=False,
    webserver=True,
):
    upstream = fetch_upstream()
    if not webserver:
        if os.path.exists(os.path.join(path, "_inspection_version.txt")):
            with open(os.path.join(path, "_inspection_version.txt")) as f:
                db_version = f.read()
        else:
            db_version = ""
        if db_version != version and os.path.exists(path):
            shutil.rmtree(path)
        if not os.path.exists(path):
            os.makedirs(path)
            with open(os.path.join(path, "_inspection_version.txt"), "w") as f:
                f.write(version)

        existing_pkg_dict = existing(path)
        fetch_and_run_function = partial(fetch_and_run, path)
    else:
        existing_pkg_dict = web_interface.get_current_extracted_pkgs()
        fetch_and_run_function = fetch_and_run_web

    # Pull up and partial this out existing_pkgs
    def diff_sort(val):
        package, dst, src_url = val
        arch = dst.split("/")[1]
        return (
            package in existing_pkg_dict,
            sort_arch_ordering.index(arch),
        )

    pkgs_to_inspect = list(diff(upstream, existing_pkg_dict))
    # shuffle so that we don't always get the same pkgs
    shuffle(pkgs_to_inspect)
    sorted_files = sorted(pkgs_to_inspect, key=diff_sort)
    print(f"TOTAL OUTSTANDING ARTIFACTS: {len(sorted_files)}")
    sorted_files = sorted_files[:number_to_reap]

    if single_thread:
        {
            fetch_and_run_function(
                package,
                dst,
                src_url,
                # progress.update
            ): (package, dst, src_url)
            for package, dst, src_url in tqdm(sorted_files)
            if (src_url not in known_bad_packages)
        }
    else:
        # This uses processes by default, which is most likely ok
        with Client():
            db.from_sequence(sorted_files).map(
                lambda x: fetch_and_run_function(*x)
            ).compute()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root_path")
    parser.add_argument(
        "--known-bad-packages",
        help="name of a json file containing a list of urls to be skipped",
    )
    parser.add_argument(
        "--debug",
        help="run without dask for debugging/speed testing",
    )
    parser.add_argument(
        "--n_artifacts", help="number of artifacts to inspect", default=5000
    )
    parser.add_argument("--local", help="to local disk for storage", default=False)

    args = parser.parse_args()
    print(args)
    if args.known_bad_packages:
        with open(args.known_bad_packages, "r") as fo:
            known_bad_packages = set(json.load(fo))
    else:
        known_bad_packages = set()

    reap(
        args.root_path,
        known_bad_packages,
        number_to_reap=int(args.n_artifacts),
        single_thread=bool(args.debug),
        webserver=not bool(args.local),
    )
