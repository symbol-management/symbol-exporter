import json
import pytest
from pathlib import Path

from symbol_exporter.ast_db_populator import fetch_and_run


@pytest.mark.skip(reason="output data model not yet stable")
def test_fetch_and_run(tmpdir):
    pkg, dst, src_url = (
        "botocore",
        "conda-forge/noarch/botocore-1.12.89-py_0.json",
        "https://conda.anaconda.org/conda-forge/noarch/botocore-1.12.89-py_0.tar.bz2",
    )
    fetch_and_run(tmpdir, pkg, dst, src_url)
    with open(f"{tmpdir}/{pkg}/{dst}") as f:
        actual = json.load(f)
    with open(Path(__file__).parent / "botocore-1.12.89-py_0.json") as f:
        expected = json.load(f)
    assert actual == expected
