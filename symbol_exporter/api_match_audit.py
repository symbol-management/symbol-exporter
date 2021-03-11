import glob
import json
import os
import shutil
from random import shuffle

import requests
from tqdm import tqdm

from symbol_exporter.api_match import find_supplying_version_set
from symbol_exporter.ast_db_populator import sort_arch_ordering, get_current_extracted_pkgs
from symbol_exporter.ast_symbol_extractor import version

audit_version = "1.1"

complete_version = f"{version}_{audit_version}"


def main(n_to_pull=10):
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

    all_extracted_artifacts = get_current_extracted_pkgs().values()
    existing_artifacts = glob.glob(f"{path}/**/*.json", recursive=True)
    existing_names = {k.partition("/")[2] for k in existing_artifacts}
    existing_pkg_names = {k.partition("/")[0] for k in existing_names}

    def not_already_audited(k):
        return k.partition("/")[2] not in existing_names

    artifacts = list(set(all_extracted_artifacts) - set(existing_names))
    # Don't have the artifacts in alphabetical order
    shuffle(artifacts)

    def diff_sort(val):
        package, channel, arch, name = val.split("/")
        return (
            package in existing_pkg_names,
            sort_arch_ordering.index(arch),
        )

    host = "https://cf-ast-symbol-table.web.cern.ch"

    for i, artifact in tqdm(
        enumerate(sorted(artifacts, key=diff_sort)), total=n_to_pull
    ):
        if i >= n_to_pull:
            break
        print(artifact)
        artifact_symbols_url = f"/api/v{version}/symbols/{artifact}"
        symbols_result = requests.get(f"{host}{artifact_symbols_url}").json()
        if not symbols_result:
            continue
        symbols = symbols_result['symbols']
        if not symbols:
            continue
        volume = set()
        for v in symbols.values():
            volume.update(v.get("data", {}).get("symbols_in_volume", set()))
        deps, bad = find_supplying_version_set(volume)
        dep_sets = [list(sorted(k)) for k in deps]

        outname = os.path.join('audit', artifact)
        os.makedirs(os.path.dirname(outname), exist_ok=True)
        with open(outname, "w") as f:
            json.dump(
                {"deps": dep_sets, "bad": list(sorted(bad))},
                f,
                indent=1,
                sort_keys=True,
            )


if __name__ == "__main__":
    main()
