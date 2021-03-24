from symbol_exporter.ast_symbol_extractor import SymbolType
from symbol_exporter.python_so_extractor import c_symbols_to_datamodel


def test__regex_conversion():
    # symbol info pulled from
    # "https://conda.anaconda.org/conda-forge/linux-64/regex-2020.5.14-py37h8f50634_0.tar.bz2"
    # "lib/python3.7/site-packages/regex/_regex.cpython-37m-x86_64-linux-gnu.so"
    actual = c_symbols_to_datamodel(
        {
            "docstring": None,
            "methods": [
                {"docstring": None, "name": "compile"},
                {"docstring": None, "name": "get_code_size"},
                {"docstring": None, "name": "get_properties"},
                {"docstring": None, "name": "fold_case"},
                {"docstring": None, "name": "get_expand_on_folding"},
                {"docstring": None, "name": "has_property_value"},
                {"docstring": None, "name": "get_all_cases"},
            ],
            "name": "_regex",
            "objects": [
                {"name": "MAGIC"},
                {"name": "CODE_SIZE"},
                {"name": "copyright"},
            ],
        }
    )
    expected = {
        "_regex": {"data": {}, "type": SymbolType.MODULE},
        "_regex.CODE_SIZE": {"data": {}, "type": SymbolType.CONSTANT},
        "_regex.MAGIC": {"data": {}, "type": SymbolType.CONSTANT},
        "_regex.compile": {"data": {}, "type": SymbolType.FUNCTION},
        "_regex.copyright": {"data": {}, "type": SymbolType.CONSTANT},
        "_regex.fold_case": {"data": {}, "type": SymbolType.FUNCTION},
        "_regex.get_all_cases": {"data": {}, "type": SymbolType.FUNCTION},
        "_regex.get_code_size": {"data": {}, "type": SymbolType.FUNCTION},
        "_regex.get_expand_on_folding": {"data": {}, "type": SymbolType.FUNCTION},
        "_regex.get_properties": {"data": {}, "type": SymbolType.FUNCTION},
        "_regex.has_property_value": {"data": {}, "type": SymbolType.FUNCTION},
    }
    assert actual == expected
