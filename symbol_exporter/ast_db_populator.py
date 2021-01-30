import ast
import glob
import io
import json
import os
import shutil
import tarfile
from concurrent.futures._base import as_completed
from tempfile import TemporaryDirectory

import requests
from libcflib.tools import expand_file_and_mkdirs
from libcflib.preloader import ReapFailure, diff
from tqdm import tqdm

from symbol_exporter.ast_symbol_extractor import SymbolFinder, version
from symbol_exporter.tools import executor


def file_path_to_import(file_path: str):
    return file_path.replace("/__init__.py", "").replace(".py", "").replace("/", ".")


def parse_code(code, module_name):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    z = SymbolFinder(module_name)
    z.visit(tree)
    return z.symbols


def single_file_extraction(python_file, top_dir):
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
        print(e)
        s = {}
    return s


def get_all_symbol_names(top_dir):
    # Note Jedi seems to pick up things that are protected by a
    # __name__ == '__main__' if statement
    # this could cause some over-reporting of viable imports this
    # shouldn't cause issues with an audit since we don't expect 3rd parties
    # to depend on those
    symbols_dict = {}
    # walk all the files looking for python files
    glob_glob = glob.glob(f"{top_dir}/**/*.py", recursive=True)
    for file_name in [k for k in glob_glob]:
        sd = single_file_extraction(file_name, top_dir)
        symbols_dict.update(sd)

    return symbols_dict


def harvest_imports(io_like):
    tf = tarfile.open(fileobj=io_like, mode="r:bz2")
    # TODO: push dir allocation into thread?
    with TemporaryDirectory() as f:
        py_members = [m for m in tf.getmembers() if m.name.endswith(".py")]
        tf.extractall(path=f, members=py_members)
        symbols = {}
        found_sp = False
        for root, subdirs, files in os.walk(f):
            if root.lower().endswith("site-packages"):
                found_sp = True
                _symbols = get_all_symbol_names(root)
                symbols.update(_symbols)
    tf.close()
    if not found_sp:
        return None
    return symbols


def reap_imports(
    root_path, package, dst_path, src_url, filelike, progress_callback=None
):
    if progress_callback:
        progress_callback()
    try:
        harvested_data = harvest_imports(filelike)
        if harvested_data:
            for k in harvested_data:
                harvested_data[k]["symbols_in_volume"] = sorted(
                    list(harvested_data[k]["symbols_in_volume"])
                )
        with open(
            expand_file_and_mkdirs(os.path.join(root_path, package, dst_path)), "w"
        ) as fo:
            json.dump(harvested_data, fo, indent=1, sort_keys=True)
        del harvested_data
    except Exception as e:
        raise ReapFailure(package, src_url, str(e))


def fetch_artifact(src_url):
    resp = requests.get(src_url, timeout=60 * 2)
    filelike = io.BytesIO(resp.content)
    return filelike


def fetch_and_run(path, pkg, dst, src_url, progess_callback=None):
    filelike = fetch_artifact(src_url)
    reap_imports(path, pkg, dst, src_url, filelike, progress_callback=progess_callback)
    filelike.close()


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


def reap(path, known_bad_packages=(), number_to_reap=1000, single_thread=False):
    if os.path.exists(os.path.join(path, "_inspection_version.txt")):
        with open(os.path.join(path, "_inspection_version.txt")) as f:
            db_version = f.read()
    if db_version != version:
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)
        with open(os.path.join(path, "_inspection_version.txt"), "w") as f:
            f.write(version)

    existing_pkgs = os.listdir(path)

    def diff_sort(val):
        package, dst, src_url = val
        arch = dst.split("/")[1]
        return (
            package in existing_pkgs,
            sort_arch_ordering.index(arch),
        )

    sorted_files = sorted(list(diff(path)), key=diff_sort)
    print(f"TOTAL OUTSTANDING ARTIFACTS: {len(sorted_files)}")
    sorted_files = sorted_files[:number_to_reap]

    if single_thread:
        futures = {
            fetch_and_run(
                path,
                package,
                dst,
                src_url,
                # progress.update
            ): (package, dst, src_url)
            for package, dst, src_url in tqdm(sorted_files)
            if (src_url not in known_bad_packages)
        }
    else:

        with executor(max_workers=5, kind="dask") as pool:
            futures = {
                pool.submit(
                    fetch_and_run,
                    path,
                    package,
                    dst,
                    src_url,
                    # progress.update
                ): (package, dst, src_url)
                for package, dst, src_url in sorted_files
                if (src_url not in known_bad_packages)
            }
            for f in tqdm(as_completed(futures), total=len(sorted_files)):
                try:
                    f.result()
                except ReapFailure as e:
                    print(f"FAILURE {e.args}")
                except Exception:
                    pass


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
        number_to_reap=1000,
        single_thread=bool(args.debug),
    )
