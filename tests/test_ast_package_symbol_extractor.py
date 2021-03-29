from symbol_exporter.ast_package_symbol_extractor import DirectorySymbolFinder
from symbol_exporter.ast_symbol_extractor import SymbolType
from symbol_exporter.db_access_model import make_json_friendly

expected = {
    "numpy.version": {"type": SymbolType.MODULE, "data": {}},
    "numpy.version.get_versions": {"type": SymbolType.FUNCTION, "data": {"lineno": 4}},
    "numpy": {"type": SymbolType.PACKAGE, "data": {}},
    "numpy.numeric": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric"},
    },
    "numpy.abs": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.absolute"},
    },
    "numpy.alias_version": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version"},
    },
    "numpy.alias_get_versions": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version.get_versions"},
    },
    "numpy.ones": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.ones"},
    },
    "numpy.absolute": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.absolute"},
    },
    "numpy.core.absolute": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.absolute"},
    },
    "numpy.core.ones": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.ones"},
    },
    "numpy.relative.*": {
        "type": SymbolType.RELATIVE_STAR_IMPORT,
        "data": {"imports": [{"shadows": "core", "level": 1, "module": "numpy.__init__"}]},
    },
    "numpy.core": {"type": SymbolType.PACKAGE, "data": {}},
    "numpy.core.relative.*": {
        "type": SymbolType.RELATIVE_STAR_IMPORT,
        "data": {"imports": [{"shadows": "numeric", "level": 1, "module": "numpy.core.__init__"}]},
    },
    "numpy.core.numeric": {"type": SymbolType.MODULE, "data": {}},
    "numpy.core.numeric.ones": {"type": SymbolType.FUNCTION, "data": {"lineno": 1}},
    "numpy.core.numeric.absolute": {
        "type": SymbolType.FUNCTION,
        "data": {"lineno": 5, "symbols_in_volume": {"abs": {"line number": [6]}}},
    },
    "numpy.get_versions": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version.get_versions"},
    },
    "numpy.core.version": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version"},
    },
    "numpy.core.abs": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.absolute"},
    },
    "numpy.core.get_versions": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version.get_versions"},
    },
    "numpy.core.alias_get_versions": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version.get_versions"},
    },
    "numpy.core.alias_version": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version"},
    },
    "numpy.core.*": {"type": SymbolType.STAR_IMPORT, "data": {"imports": {"json"}}},
    "numpy.*": {"type": SymbolType.STAR_IMPORT, "data": {"imports": {"requests"}}},
    "numpy.version.*": {
        "type": SymbolType.STAR_IMPORT,
        "data": {"imports": {"os"}},
    },
}


def test_deref_star():
    import json
    import sys

    dsf = DirectorySymbolFinder("../tests/numpy")
    symbols = dsf.extract_symbols()
    json.dump(symbols, sys.stdout, indent=2, default=make_json_friendly)
    assert symbols == expected
