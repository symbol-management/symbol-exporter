"""Audit to derived the expected dependencies and version ranges for all extracted packages"""
import glob
import json
import os
import shutil
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from random import shuffle

import requests
from tqdm import tqdm

from symbol_exporter.api_match import find_supplying_version_set
from symbol_exporter.ast_db_populator import make_json_friendly
from symbol_exporter.ast_symbol_extractor import version
from symbol_exporter.db_access_model import WebDB

audit_version = "2.1"

complete_version = f"{version}_{audit_version}"

web_interface = WebDB()


def inner_loop(artifact):
    symbols = web_interface.get_artifact_symbols(artifact)
    if not symbols:
        return None
    volume = set()
    for v in symbols.values():
        volume.update(v.get("data", {}).get("symbols_in_volume", set()))
    # pull out self symbols, since we assume those are gotten locally and self consistent
    volume -= set(symbols)
    deps, bad = find_supplying_version_set(volume)
    return deps, bad


def inner_loop_and_write(artifact):
    result = inner_loop(artifact)
    if result is None:
        output = None
    else:
        dep_sets, bad = result
        output = {"deps": dep_sets, "bad": list(sorted(bad))}
    outname = os.path.join("audit", artifact)
    os.makedirs(os.path.dirname(outname), exist_ok=True)
    with open(outname, "w") as f:
        json.dump(output, f, indent=1, sort_keys=True, default=make_json_friendly)


def main(n_to_pull=1000):
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
    existing_artifact_names = {k.partition("/")[2].replace('.json', '') for k in existing_artifacts}

    artifacts = sorted(list(set(all_extracted_artifacts) - set(existing_artifact_names)))

    # Don't have the artifacts in alphabetical order
    shuffle(artifacts)

    with ThreadPoolExecutor() as pool:
        futures = [pool.submit(inner_loop_and_write, artifact) for artifact in artifacts[:n_to_pull]]
        for future in tqdm(as_completed(futures), total=n_to_pull):
            try:
                future.result()
            except requests.exceptions.ConnectionError:
                pass


if __name__ == "__main__":
    main()
