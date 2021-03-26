import requests
from os.path import basename
import hashlib
import shutil
import pathlib

from conda_package_handling import api as cph_api
import pytest

from symbol_exporter.python_so_extractor import CompiledPythonLib

CACHE_DIR = pathlib.Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)


def compare(url, checksum, filename, expected, *, xmissing=False):
    package_dir = download_sample(url, checksum)

    results = CompiledPythonLib(package_dir / filename).find_symbols()
    actual = {x["name"] for x in results["methods"]}
    actual |= {x["name"] for x in results["objects"]}
    diff = actual - expected
    assert not diff, (f"Found {len(diff)} extra keys", diff)
    diff = expected - actual
    if xmissing:
        assert diff, "Unexpectedly passed!"
        pytest.xfail(f"{len(diff)} out of {len(expected)} were not found (known issue)")
    else:
        assert not diff, (
            f"Failed to find {len(diff)} out of {len(expected)} keys",
            diff,
        )


def download_sample(url, checksum):
    filename = CACHE_DIR / basename(url)
    if not filename.exists():
        print(f"Downloading {url}")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with filename.open("wb") as f:
                shutil.copyfileobj(r.raw, f)

    md5 = hashlib.md5()
    with filename.open("rb") as f:
        while data := f.read(1024 ** 2):
            md5.update(data)
    if md5.hexdigest() != checksum:
        raise RuntimeError(f"Hash mismatch for {filename}, expected {checksum} got {md5.hexdigest()}")

    target_dir = pathlib.Path(str(filename).replace(".tar.bz2", "").replace(".conda", ""))
    if not target_dir.is_dir():
        cph_api.extract(str(filename), str(target_dir))

    return target_dir
