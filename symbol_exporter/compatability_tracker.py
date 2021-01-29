import csv
import glob
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from conda.models.version import VersionOrder


def get_data(file):
    with open(file) as f:
        data = json.load(f)
    if data:
        return set(data["symbols"])
    else:
        return set()


def compute_symbol_compat_table(pkg):
    all_files = sorted(list(glob.glob(f"symbols/{pkg}/**/*.json", recursive=True)))
    symbols_by_ver_arch = defaultdict(dict)
    for file in all_files:
        _, pkg, channel, arch, name = file.split(os.sep)
        _pkg, ver, build = name.replace(".json", "").rsplit("-", 2)
        with open(file) as f:
            j = json.load(f)
        if not j or "symbols" not in j:
            continue
        symbols_by_ver_arch[arch][ver] = set(j["symbols"])
    arch_csv_data = {}
    for arch in symbols_by_ver_arch:
        csv_data = []
        for ver in sorted(symbols_by_ver_arch[arch], key=VersionOrder):
            symbols = symbols_by_ver_arch[arch][ver]
            data = {
                "version": ver,
                "number of symbols": len(symbols),
                "symbols": symbols,
            }
            if len(csv_data) == 0:
                data.update({"added symbols": None, "removed symbols": None})
            else:
                previous_symbols = csv_data[-1]["symbols"]
                data.update(
                    {
                        "added symbols": len(symbols - previous_symbols),
                        "removed symbols": len(previous_symbols - symbols),
                    }
                )
            csv_data.append(data)
        os.makedirs(f"symbol_counts/{pkg}", exist_ok=True)
        with open(f"symbol_counts/{pkg}/{arch}.csv", "w") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=[
                    "version",
                    "number of symbols",
                    "added symbols",
                    "removed symbols",
                ],
            )
            writer.writeheader()
            for data in reversed(csv_data):
                data.pop("symbols")
                writer.writerow(data)
        arch_csv_data[arch] = csv_data
    return arch_csv_data


if __name__ == "__main__":
    done_files_store = ".compat_indexed_files"

    try:
        with open(done_files_store, "r") as f:
            indexed_files = {ff.strip() for ff in f.readlines()}
    except FileNotFoundError:
        indexed_files = set()

    futures = {}
    all_files = set(glob.glob("symbols/**/*.json", recursive=True))
    new_files = all_files - indexed_files

    updated_pkgs = set()

    for file in new_files:
        _, pkg, channel, arch, name = file.split(os.sep)
        updated_pkgs.add(pkg)

    with ThreadPoolExecutor() as pool:
        for pkg in updated_pkgs:
            pool.submit(compute_symbol_compat_table, pkg)

    with open(done_files_store, "a") as f:
        for file in new_files:
            f.write(f"{file}\n")
