import hashlib
import hmac
import json
import os
from datetime import datetime
from enum import Enum

import dask.bag as db
from dask.distributed import Client
import requests
from requests.exceptions import ChunkedEncodingError

from symbol_exporter.ast_symbol_extractor import version


class WebDB:
    def __init__(self, host="https://cf-ast-symbol-table.web.cern.ch"):
        self.host = host
        raw_token = os.environ.get("STORAGE_SECRET_TOKEN", "")
        if raw_token == "":
            print("No token only pulls allowed")
        self.secret_token = raw_token.encode("utf-8")

    def _dumps(self, data):
        return json.dumps(data, default=make_json_friendly, sort_keys=True)
    
    def _push(self, data, url):
        dumped_data = self._dumps(data)
        dumped_metadata = self._dumps(data['metadata'])
        r = requests.put(
            f"{self.host}{url}",
            data=dumped_data,
            headers=self._setup_headers(dumped_data, url=url, dumped_metadata=dumped_metadata),
            params=dict(metadata=dumped_metadata)
        )
        r.raise_for_status()

    def _setup_headers(self, dumped_data, url, dumped_metadata):
        headers = {
            "X-Signature-Timestamp": datetime.utcnow().isoformat(),
            "X-Body-Signature": hmac.new(self.secret_token, dumped_data.encode(), hashlib.sha256).hexdigest(),
        }
        headers["X-Headers-Signature"] = hmac.new(
            self.secret_token,
            b"".join(
                [
                    url.encode(),
                    headers["X-Signature-Timestamp"].encode(),
                    headers["X-Body-Signature"].encode(),
                    dumped_metadata.encode()
                ]
            ),
            hashlib.sha256,
        ).hexdigest()
        return headers

    def push_symbol_table(self, top_level_name, symbol_table):
        url = f"/api/v{version}/symbol_table/{top_level_name}"
        self._push(symbol_table, url)

    def get_current_symbol_table_artifacts_by_top_level(self):
        all_indexted_pkgs = {}
        extracted_symbols = self.get_symbol_table("")
        with Client(threads_per_worker=100):
            [
                all_indexted_pkgs.update({k: set(v)})
                for k, v in zip(
                    extracted_symbols,
                    db.from_sequence(extracted_symbols)
                    .map(self.get_symbol_table_metadata)
                    .map(lambda x: x.get("indexed artifacts", {}))
                    .compute(),
                )
            ]
        return all_indexted_pkgs

    def get_symbol_table(self, top_level_name):
        symbol_table_url = f"/api/v{version}/symbol_table/{top_level_name.lower()}"
        try:
            return requests.get(f"{self.host}{symbol_table_url}").json()
        except (
            requests.exceptions.ConnectionError,
            ChunkedEncodingError,
            json.decoder.JSONDecodeError,
        ):
            return {}
    
    def get_symbol_table_metadata(self, top_level_name):
        symbol_table_url = f"/api/v{version}/symbol_table/{top_level_name.lower()}/metadata"
        try:
            return requests.get(f"{self.host}{symbol_table_url}").json()
        except (
            requests.exceptions.ConnectionError,
            ChunkedEncodingError,
            json.decoder.JSONDecodeError,
        ):
            return {}

    def get_artifact_metadata(self, artifact_name):
        artifact_symbols_url = f"/api/v{version}/symbols/{artifact_name}/metadata"
        result = requests.get(f"{self.host}{artifact_symbols_url}").json()
        return result.get("metadata", {}) if result else {}

    def get_top_level_symbols(self, artifact_name):
        artifact_symbols_url = f"/api/v{version}/symbols/{artifact_name}/metadata"
        result = requests.get(f"{self.host}{artifact_symbols_url}").json()
        if not result:
            return set()
        return result.get("top level symbols")

    def get_artifact_symbols(self, artifact_name):
        artifact_symbols_url = f"/api/v{version}/symbols/{artifact_name}"
        result = requests.get(f"{self.host}{artifact_symbols_url}").json()
        return result.get("symbols", {}) if result else {}

    def get_current_extracted_pkgs(self):
        url = f"/api/v{version}/symbols"
        paths = requests.get(f"{self.host}{url}").json()
        path_by_pkg = {path.split("/")[0]: path for path in paths}
        return path_by_pkg

    def send_to_webserver(self, data, package, dst_path):
        # BSD 3-Clause License
        #
        # Copyright (c) 2021, Chris Burr
        # All rights reserved.
        #
        # Redistribution and use in source and binary forms, with or without
        # modification, are permitted provided that the following conditions are met:
        #
        # * Redistributions of source code must retain the above copyright notice, this
        #   list of conditions and the following disclaimer.
        #
        # * Redistributions in binary form must reproduce the above copyright notice,
        #   this list of conditions and the following disclaimer in the documentation
        #   and/or other materials provided with the distribution.
        #
        # * Neither the name of the copyright holder nor the names of its
        #   contributors may be used to endorse or promote products derived from
        #   this software without specific prior written permission.
        #
        # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        # AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
        # IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        # DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
        # FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
        # DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
        # SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        # CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
        # OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        if not data:
            data = None

        url = f"/api/v{version}/symbols/{package}/{dst_path}".replace(".json", "")
        # Upload the data
        self._push(data, url)


def make_json_friendly(data):
    if isinstance(data, set):
        return list(sorted(data))
    if isinstance(data, Enum):
        return str(data)
    return data
