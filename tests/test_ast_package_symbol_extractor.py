import pytest

from symbol_exporter.ast_package_symbol_extractor import DirectorySymbolFinder
from symbol_exporter.ast_symbol_extractor import SymbolType

expected_does_not_handle_multiple_level_relative_imports = {
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
    # We do not handle these two use cases yet
    # These are relative star imports in a relatively imported file
    # that need to be bubbled up to top level namespace.
    # "numpy.ones": {
    #     "type": SymbolType.RELATIVE_IMPORT,
    #     "data": {"shadows": "numpy.core.numeric.ones"},
    # },
    # "numpy.absolute": {
    #     "type": SymbolType.RELATIVE_IMPORT,
    #     "data": {"shadows": "numpy.core.numeric.absolute"},
    # },
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
    "numpy.*": {"type": SymbolType.STAR_IMPORT, "data": {"imports": {"requests", "json"}}},
    "numpy.version.*": {
        "type": SymbolType.STAR_IMPORT,
        "data": {"imports": {"os"}},
    },
}


def test_relative_imports_does_not_handle_multiple_levels():
    dsf = DirectorySymbolFinder("tests/numpy")
    symbols = dsf.extract_symbols()
    assert symbols == expected_does_not_handle_multiple_level_relative_imports


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
    "numpy.*": {"type": SymbolType.STAR_IMPORT, "data": {"imports": {"requests", "json"}}},
    "numpy.version.*": {
        "type": SymbolType.STAR_IMPORT,
        "data": {"imports": {"os"}},
    },
}


@pytest.mark.skip(reason="work in progress")
def test_relative_imports_with_multiple_levels():
    dsf = DirectorySymbolFinder("../tests/numpy")
    symbols = dsf.extract_symbols()
    assert symbols == expected
