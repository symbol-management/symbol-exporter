import json
import pytest
from pathlib import Path

from symbol_exporter.ast_db_populator import fetch_and_run, fetch_artifact, harvest_imports


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
    ('conda-forge/linux-64/python-3.9.1-hffdb5ce_0_cpython', {'math', 'math.sin'}),
    ('conda-forge/linux-64/regex-2020.5.14-py37h8f50634_0.tar.bz2', {
        "fold_case",
        "copyright",
        "has_property_value",
        "get_expand_on_folding",
        "compile",
        "MAGIC",
        "CODE_SIZE",
        "get_properties",
        "get_all_cases",
        "get_code_size",
    })
])
def test_harvest(pkg_path, expected_set):
    src_url = f"https://conda.anaconda.org/{pkg_path}.tar.bz2"
    filelike = fetch_artifact(src_url)
    harvested_data = harvest_imports(filelike)
    assert expected_set.issubset(set(harvested_data['symbols']))
