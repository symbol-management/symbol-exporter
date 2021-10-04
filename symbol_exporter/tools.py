"""Tooling from third parties with motifications"""
import contextlib
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

from collections import defaultdict
import requests
import json
import bz2
import io
import os
import glob
from xonsh.tools import expand_path

try:
    from conda.models.version import normalized_version
except ImportError:
    from packaging import version as packaging_version

    def normalized_version(x):
        return packaging_version.parse(x)


"""
BSD 3-clause license
Copyright (c) 2015-2018, NumFOCUS
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


@contextlib.contextmanager
def executor(kind: str, max_workers: int, daemon=True):
    """General purpose utility to get an executor with its as_completed handler

    This allows us to easily use other executors as needed.
    """
    if kind == "thread":
        with ThreadPoolExecutor(max_workers=max_workers) as pool_t:
            yield pool_t
    elif kind == "process":
        with ProcessPoolExecutor(max_workers=max_workers) as pool_p:
            yield pool_p
    elif kind in ["dask", "dask-process", "dask-thread"]:
        import dask
        import distributed
        from distributed.cfexecutor import ClientExecutor

        processes = kind == "dask" or kind == "dask-process"

        with dask.config.set({"distributed.worker.daemon": daemon}):
            with distributed.LocalCluster(
                n_workers=max_workers,
                processes=processes,
                # silence_logs='error'
            ) as cluster:
                with distributed.Client(cluster) as client:
                    yield ClientExecutor(client)
    else:
        raise NotImplementedError("That kind is not implemented")


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


def diff(upstream, local):
    missing_files = set()

    missing_packages = set(upstream.keys()) - set(local.keys())
    present_packages = set(upstream.keys()) & set(local.keys())

    for package in missing_packages:
        missing_files.update((package, k, v) for k, v in upstream[package].items())

    for package in present_packages:
        upstream_artifacts = upstream[package]
        present_artifacts = local[package]

        missing_artifacts = set(upstream_artifacts) - set(present_artifacts)
        missing_files.update((package, k, v) for k, v in upstream_artifacts.items() if k in missing_artifacts)

    return missing_files


channel_list = [
    "https://conda.anaconda.org/conda-forge/linux-64",
    "https://conda.anaconda.org/conda-forge/noarch",
    # "https://conda.anaconda.org/conda-forge/osx-64",
    # "https://conda.anaconda.org/conda-forge/win-64",
    # "https://conda.anaconda.org/conda-forge/linux-ppc64le",
    # "https://conda.anaconda.org/conda-forge/linux-aarch64",
    # "https://conda.anaconda.org/conda-forge/osx-arm64",
]


def fetch_arch(arch, conditional=None):
    # Generate a set a urls to generate for an channel/arch combo
    print(f"Fetching {arch}")
    r = requests.get(f"{arch}/repodata.json.bz2")
    repodata = json.load(bz2.BZ2File(io.BytesIO(r.content)))
    for p, v in repodata["packages"].items():
        package_url = f"{arch}/{p}"
        file_name = package_url.replace("https://conda.anaconda.org/", "").replace(".tar.bz2", ".json")
        if conditional is None or conditional(v):
            yield v["name"], file_name, package_url


def fetch_upstream(conditional=None):
    package_urls = defaultdict(dict)
    for channel_arch in channel_list:
        for package_name, filename, url in fetch_arch(channel_arch, conditional=conditional):
            package_urls[package_name][filename] = url
    return package_urls


class ReapFailure(Exception):
    def __init__(self, package, src_url, msg):
        super(ReapFailure, self).__init__(package, src_url, msg)


def recursive_ls(root):
    packages = os.listdir(root)
    for p in packages:
        files = glob.glob(f"{root}/{p}/*/*/*.json")
        for f in files:
            yield p, f.replace(f"{root}/{p}/", "")


def existing(path, recursive_ls=recursive_ls):
    existing_dict = defaultdict(set)
    for pak, path in recursive_ls(path):
        existing_dict[pak].add(path)
    return existing_dict


def expand_file_and_mkdirs(x):
    """Expands a variable that represents a file, and ensures that the
    directory it lives in actually exists.
    """
    x = os.path.abspath(expand_path(x))
    d = os.path.dirname(x)
    os.makedirs(d, exist_ok=True)
    return x


def find_version_ranges(all_versions, acceptable_versions):
    _all_versions = sorted(map(normalized_version, all_versions))
    _acceptable_versions = sorted(map(normalized_version, acceptable_versions))
    range_endpoints = []
    current_range = []
    # TODO: speed up this loop by only going over acceptable versions,
    # and asking if current version is same as previous version index +1 in all versions
    for version in _all_versions:
        if version in _acceptable_versions:
            if not current_range:
                current_range = [version, version]
            current_range[-1] = version
        else:
            range_endpoints.append(tuple(current_range))
            current_range = []
    if current_range:
        range_endpoints.append(tuple(current_range))
    ranges = []
    for lower, higher in filter(bool, range_endpoints):
        if higher == _all_versions[-1]:
            ranges.append(f">={lower}")
        elif lower != higher:
            ranges.append(f">={lower},<={higher}")
        else:
            ranges.append(f"{lower}")
    return "|".join(ranges)
