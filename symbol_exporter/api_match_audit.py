"""Audit to derived the expected dependencies and version ranges for all extracted packages"""
import bz2
import glob
import io
import json
import os
import shutil
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from random import shuffle
from distributed.client import Client
import dask.bag as db

import requests
from tqdm import tqdm

from symbol_exporter.api_match import extract_artifacts_from_deps, find_supplying_version_set
from symbol_exporter.ast_db_populator import make_json_friendly
from symbol_exporter.ast_symbol_extractor import version, builtin_symbols
from symbol_exporter.db_access_model import WebDB
from symbol_exporter.tools import channel_list, find_version_ranges

audit_version = "2.3"

complete_version = f"{version}_{audit_version}"

web_interface = WebDB()


existing_versions_by_package = {}
for channel in channel_list:
    r = requests.get(f"{channel}/repodata.json.bz2")
    repodata = json.load(bz2.BZ2File(io.BytesIO(r.content)))
    for p, v in repodata["packages"].items():
        existing_versions_by_package.setdefault(v["name"], set()).add(v["version"])


def inner_loop(artifact):
    symbols = web_interface.get_artifact_symbols(artifact)
    if not symbols:
        return None
    volume = set()
    for v in symbols.values():
        volume.update(v.get("data", {}).get("symbols_in_volume", set()))
    # pull out self symbols, since we assume those are gotten locally and self consistent
    volume -= set(symbols)
    volume -= set(builtin_symbols)
    deps, bad = find_supplying_version_set(volume)
    return deps, bad


def inner_loop_and_write(artifact):
    result = inner_loop(artifact)
    if result is None:
        output = None
    else:
        dep_sets, bad = result
        versions_by_package = extract_artifacts_from_deps(dep_sets)
        version_ranges_by_package = {}
        missing_versions_by_package = {}
        for package, versions in versions_by_package.items():
            version_ranges_by_package[package] = find_version_ranges(existing_versions_by_package[package], versions)
            missing_versions_by_package[package] = set(existing_versions_by_package[package]) - set(versions)
        output = {
            "deps": dep_sets,
            "bad": list(sorted(bad)),
            "version_ranges": [
                f"{package} {version_range}" for package, version_range in version_ranges_by_package.items()
            ],
            "missing_versions": missing_versions_by_package,
        }
    outname = os.path.join("audit", artifact)
    os.makedirs(os.path.dirname(outname), exist_ok=True)
    with open(outname, "w") as f:
        json.dump(output, f, indent=1, sort_keys=True, default=make_json_friendly)


def main(n_to_pull=100):
    path = "audit"

    if os.path.exists(os.path.join(path, "_inspection_version.txt")):
        with open(os.path.join(path, "_inspection_version.txt")) as f:
            db_version = f.read()
    else:
        db_version = ""
    if db_version != complete_version and os.path.exists(path):
        shutil.rmtree(path)

    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, "_inspection_version.txt"), "w") as f:
        f.write(complete_version)

    all_extracted_artifacts = web_interface.get_current_extracted_pkgs().values()
    existing_artifacts = glob.glob(f"{path}/**/*.json", recursive=True)
    existing_artifact_names = {k.partition("/")[2].replace(".json", "") for k in existing_artifacts}

    artifacts = sorted(list(set(all_extracted_artifacts) - set(existing_artifact_names)))

    # Don't have the artifacts in alphabetical order
    shuffle(artifacts)

    with Client(threads_per_worker=100):
        db.from_sequence(artifacts[:n_to_pull]).map(inner_loop_and_write).compute()


if __name__ == "__main__":
    main()
