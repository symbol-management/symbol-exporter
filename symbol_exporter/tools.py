import contextlib
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

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
            ) as cluster:
                with distributed.Client(cluster, silence_logs='error') as client:
                    yield ClientExecutor(client)
    else:
        raise NotImplementedError("That kind is not implemented")