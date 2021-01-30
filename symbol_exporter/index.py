"""
BSD 3-Clause License

Copyright (c) 2018, Re(search) Gro(up)
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import glob
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby
from pathlib import Path

from libcflib.jsonutils import dump, load
from tqdm import tqdm


def get_data(file):
    with open(file) as f:
        data = json.load(f)
    if data:
        return set(data["symbols"])
    else:
        return set()


def read_sharded_dict():
    d = {}
    for file in os.listdir("symbol_table"):
        with open(file) as f:
            d.update(load(f))
    return d


def write_out_maps(gn, import_map):
    try:
        with open(f"symbol_table/{gn}.json", "r") as f:
            old_map = load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        old_map = import_map
    else:
        for k in list(import_map):
            old_map.setdefault(k, set()).update(import_map.pop(k))
    with open(f"symbol_table/{gn}.json", "w") as f:
        dump(old_map, f)


if __name__ == "__main__":
    symbol_table = defaultdict(set)

    try:
        with open(".indexed_files", "r") as f:
            indexed_files = {ff.strip() for ff in f.readlines()}
    except FileNotFoundError:
        indexed_files = set()

    futures = {}
    tpe = ThreadPoolExecutor()
    all_files = set(glob.glob("symbols/**/*.json", recursive=True))
    new_files = all_files - indexed_files

    for file in new_files:
        artifact_name = Path(file).name.rsplit(".", 1)[0]
        for symbol in get_data(file):
            symbol_table[symbol].add(artifact_name)

    # for file in new_files:
    #     artifact_name = Path(file).name.rsplit(".", 1)[0]
    #     futures[tpe.submit(get_data, file)] = artifact_name
    #
    # for future in tqdm(as_completed(futures), total=len(futures)):
    #     f = futures.pop(future)
    #     for symbol in future.result():
    #         symbol_table[symbol].add(f)

    os.makedirs("symbol_table", exist_ok=True)
    sorted_imports = sorted(symbol_table.keys(), key=lambda x: x.lower())

    # with tpe as pool:
    #     for gn, keys in tqdm(groupby(sorted_imports, lambda x: x[:2].lower())):
    #         sub_import_map = {k: symbol_table.pop(k) for k in keys}
    #         pool.submit(write_out_maps, gn, sub_import_map)

    for gn, keys in tqdm(groupby(sorted_imports, lambda x: x[:2].lower())):
        sub_import_map = {k: symbol_table.pop(k) for k in keys}
        write_out_maps(gn, sub_import_map)

    with open(".indexed_files", "a") as f:
        for file in new_files:
            f.write(f"{file}\n")
