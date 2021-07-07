import pytest

from symbol_exporter.ast_package_symbol_extractor import DirectorySymbolFinder
from symbol_exporter.ast_symbol_extractor import SymbolType

expected = {
    "numpy.version": {"type": SymbolType.MODULE, "data": {"symbols_in_volume": {"os": {"line number": [1]}}}},
    "numpy.version.get_versions": {
        "type": SymbolType.FUNCTION, 
        "data": {"lineno": 5, "symbols_in_volume": {"numpy.core.numeric": {"line number": [6]}}}
        },
    "numpy": {"type": SymbolType.PACKAGE, "data": {"symbols_in_volume": {"requests": {"line number": [5]}}}},
    "numpy.numeric": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric"},
    },
    "numpy.version.numeric": {
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
    "numpy.~~RELATIVE~~.*": {
        "type": SymbolType.RELATIVE_STAR_IMPORT,
        "data": {"imports": ["numpy.core"]},
    },
    "numpy.core": {"type": SymbolType.PACKAGE, "data": {"symbols_in_volume": {"json": {"line number": [8]}}}},
    "numpy.core.~~RELATIVE~~.*": {
        "type": SymbolType.RELATIVE_STAR_IMPORT,
        "data": {"imports": ["numpy.core.numeric"]},
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
    "numpy.*": {"type": SymbolType.STAR_IMPORT, "data": {"imports": {"requests", "json"}}},
    "numpy.version.*": {
        "type": SymbolType.STAR_IMPORT,
        "data": {"imports": {"os"}},
    },
    "numpy.c2.triple": {"type": SymbolType.MODULE, "data": {}},
    "numpy.c2.triple.version": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version"},
    },
    "numpy.c2.triple.get_versions": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version.get_versions"},
    },
    "numpy.c2.triple.core": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core"},
    },
    "numpy.c2.triple.numeric": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric"},
    },
    "numpy.c2.triple.abs": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.absolute"},
    },
    "numpy.c2.triple.alias_version": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version"},
    },
    "numpy.c2.triple.alias_get_versions": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.version.get_versions"},
    },
    "numpy.c2.triple.*": {
        "type": SymbolType.STAR_IMPORT,
        "data": {"imports": {"requests", "json"}},
    },
    "numpy.c2.triple.~~RELATIVE~~.*": {
        "type": SymbolType.RELATIVE_STAR_IMPORT,
        "data": {"imports": ["numpy"]},
    },
    "numpy.c2.triple.ones": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.ones"},
    },
    "numpy.c2.triple.absolute": {
        "type": SymbolType.RELATIVE_IMPORT,
        "data": {"shadows": "numpy.core.numeric.absolute"},
    },
    "numpy.core.stars": {"data": {}, "type": SymbolType.MODULE},
    "numpy.core.stars.~~RELATIVE~~.*": {
        "data": {"imports": ["numpy.__init__", "numpy.core.__init__"]},
        "type": SymbolType.RELATIVE_STAR_IMPORT,
    },
}


def test_relative_imports_with_multiple_levels():
    dsf = DirectorySymbolFinder("tests/numpy")
    symbols = dsf.extract_symbols()
    assert symbols == expected
