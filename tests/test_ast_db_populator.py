import json
import pytest
import logging
from pathlib import Path

from symbol_exporter.ast_db_populator import fetch_and_run, fetch_artifact, harvest_imports
from symbol_exporter.python_so_extractor import logger

logger.setLevel(logging.ERROR)

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


@pytest.mark.parametrize('pkg_path,expected_set', [
    ('conda-forge/linux-64/python-3.9.1-hffdb5ce_0_cpython', {'math', 'math.sin', 'os'}),
    ('conda-forge/linux-64/yt-3.6.1-py39h16ac069_0', 
    {"yt.analysis_modules.halo_finding.fof.EnzoFOF.RunFOF"}
    )
])
def test_harvest(pkg_path, expected_set):
    src_url = f"https://conda.anaconda.org/{pkg_path}.tar.bz2"
    filelike = fetch_artifact(src_url)
    harvested_data = harvest_imports(filelike)
    for k in expected_set:
        assert k in harvested_data['symbols']
