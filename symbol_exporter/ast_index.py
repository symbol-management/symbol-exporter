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
import hashlib
import hmac
import json
import os
import shutil
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

from datetime import datetime
from itertools import groupby
from random import shuffle

import requests
from libcflib.jsonutils import dump, load
from tqdm import tqdm

from symbol_exporter.ast_db_populator import (
    get_current_extracted_pkgs,
    make_json_friendly,
)
from symbol_exporter.ast_symbol_extractor import version


def get_data(file):
    with open(file) as f:
        data = json.load(f)
    if data:
        return set(data)
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


def check_if_table_is_current(path):
    if os.path.exists(os.path.join(path, "_inspection_version.txt")):
        with open(os.path.join(path, "_inspection_version.txt")) as f:
            db_version = f.read()
    else:
        db_version = ""
    if db_version != version and os.path.exists(path):
        shutil.rmtree(path)
        with open(".indexed_files", "w") as f:
            pass
    if not os.path.exists(path):
        os.makedirs(path)
        with open(os.path.join(path, "_inspection_version.txt"), "w") as f:
            f.write(version)


def _pull_symbol_table_indexed_artifacts(host, symbol_entry):
    return (
        requests.get(f"{host}/api/v{version}/symbol_table/{symbol_entry}")
        .json()
        .get("metadata", {})
        .get("indexed artifacts", [])
    )


def get_current_symbol_table_artifacts():
    all_indexted_pkgs = set()
    host = "https://cf-ast-symbol-table.web.cern.ch"
    symbol_table_url = f"/api/v{version}/symbol_table"
    extracted_symbols = requests.get(f"{host}{symbol_table_url}").json()
    print("getting current symbol table artifacts")
    pool = ThreadPoolExecutor()
    futures = {
        pool.submit(
            _pull_symbol_table_indexed_artifacts, host, symbol_entry
        ): symbol_entry
        for symbol_entry in tqdm(extracted_symbols)
    }
    for future in tqdm(as_completed(futures), total=len(futures)):
        try:
            all_indexted_pkgs.update(future.result())
        # If we can't get the results we'll just push a new one up
        except Exception as e:
            print(futures[future], e)
            pass
    pool.shutdown()
    return all_indexted_pkgs


def get_symbol_table(top_level_name):
    host = "https://cf-ast-symbol-table.web.cern.ch"
    symbol_table_url = f"/api/v{version}/symbol_table/{top_level_name}"
    try:
        results = requests.get(f"{host}{symbol_table_url}").json()
    except Exception as e:
        print(top_level_name, e)
        results = {}
    return results


def get_artifact_symbols(artifact_name):
    host = "https://cf-ast-symbol-table.web.cern.ch"
    artifact_symbols_url = f"/api/v{version}/symbols/{artifact_name}"
    result = requests.get(f"{host}{artifact_symbols_url}").json()
    return result.get("symbols", {}) if result else {}


def push_symbol_table(top_level_name, symbol_table):
    host = "https://cf-ast-symbol-table.web.cern.ch"
    secret_token = os.environ["STORAGE_SECRET_TOKEN"].encode("utf-8")
    url = f"/api/v{version}/symbol_table/{top_level_name}"

    # Generate the signature
    dumped_data = json.dumps(symbol_table, default=make_json_friendly, sort_keys=True)
    headers = {
        "X-Signature-Timestamp": datetime.utcnow().isoformat(),
        "X-Body-Signature": hmac.new(
            secret_token, dumped_data.encode(), hashlib.sha256
        ).hexdigest(),
    }
    headers["X-Headers-Signature"] = hmac.new(
        secret_token,
        b"".join(
            [
                url.encode(),
                headers["X-Signature-Timestamp"].encode(),
                headers["X-Body-Signature"].encode(),
            ]
        ),
        hashlib.sha256,
    ).hexdigest()

    # Upload the data
    r = requests.put(
        f"{host}{url}",
        data=dumped_data,
        headers=headers,
    )
    r.raise_for_status()


def inner_loop(artifact_name):
    symbols = get_artifact_symbols(artifact_name)
    for top_level_name, keys in groupby(
        sorted(symbols), lambda x: x.partition(".")[0].lower()
    ):
        # carve out for star imports which don't have dots
        if top_level_name == "*":
            continue
        # download the existing symbol table
        symbol_table_with_metadata = get_symbol_table(top_level_name)
        symbol_table = symbol_table_with_metadata.get("symbol table", {})
        metadata = symbol_table_with_metadata.get("metadata", {})
        # update the symbol table
        for k in list(symbols):
            symbol_table.setdefault(k, []).append(artifact_name)
        # add artifacts to metadata
        metadata["version"] = version
        metadata.setdefault("indexed artifacts", []).append(artifact_name)
        # push back to server
        push_symbol_table(
            top_level_name, {"symbol table": symbol_table, "metadata": metadata}
        )


if __name__ == "__main__":
    extracted_artifacts = get_current_symbol_table_artifacts()
    all_artifacts = get_current_extracted_pkgs().values()
    artifacts_to_index = list(set(all_artifacts) - set(extracted_artifacts))
    print(f"Number of artifacts to index: {len(artifacts_to_index)}")

    # The shuffle here is to try to not have two threads running on the same symbol table json at once if possible
    shuffle(artifacts_to_index)
    pool = ThreadPoolExecutor()
    # Note that this is a race condition here, two threads could try to write to the same symbol table
    # however one of those will win so next round there will be one added safely and this continues
    # until none are left to be added
    print("issuing futures")
    futures = {
        pool.submit(inner_loop, artifact_name): artifact_name
        for artifact_name in tqdm(artifacts_to_index[:1000])
    }
    print("awaiting futures")
    for future in tqdm(as_completed(futures), total=len(futures)):
        print(futures[future])
        try:
            future.result()
        except Exception as e:
            print(e)
    pool.shutdown()

    # import glob
    # from collections import defaultdict
    # from concurrent.futures import ThreadPoolExecutor
    # from pathlib import Path

    # symbol_table = defaultdict(set)
    # path = "symbol_table"
    #
    # check_if_table_is_current(path)
    #
    # try:
    #     with open(".indexed_files", "r") as f:
    #         indexed_files = {ff.strip() for ff in f.readlines()}
    # except FileNotFoundError:
    #     indexed_files = set()
    #
    # futures = {}
    # tpe = ThreadPoolExecutor()
    # all_files = set(glob.glob("symbols/**/*.json", recursive=True))
    # new_files = all_files - indexed_files
    #
    # for file in new_files:
    #     artifact_name = Path(file).name.rsplit(".", 1)[0]
    #     for symbol in get_data(file):
    #         symbol_table[symbol].add(artifact_name)
    #
