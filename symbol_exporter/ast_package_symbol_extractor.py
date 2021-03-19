import ast
from pathlib import Path
from typing import Union

from symbol_exporter.ast_symbol_extractor import SymbolFinder, is_relative_import


def is_package(directory: Path) -> bool:
    # Only handles regular packages, not namespace packages. See PEP-420.
    return (directory / "__init__.py").exists()


def parse(module: Path, module_path: str) -> dict:
    code = module.read_text()  # TODO: need to check for multiple encodings
    tree = ast.parse(code)
    z = SymbolFinder(module_name=f"{module_path}.{module.stem}")
    z.visit(tree)
    return z.post_process_symbols()


def merge_dicts(*dicts):
    new_symbols = {}
    for d in dicts:
        new_symbols |= d
    return new_symbols


def relative_imports(package_symbols: dict) -> list:
    return [(k, v) for k, v in package_symbols.items() if is_relative_import(v)]


def dereference_relative_import(symbol_name: str, data: dict) -> str:
    """Expects data of a relative import"""
    shadows = data["shadows"]
    level = data["level"]
    parent = symbol_name.split(".")[:-level]
    return ".".join([*parent, shadows])


def remove_shadowed_relative_imports(package_symbols: dict):
    for k, v in relative_imports(package_symbols):
        if "__init__" in k:
            new_symbol = k.replace(".__init__", "")
            if (
                new_symbol not in package_symbols
                and f"{new_symbol}.__init__" not in package_symbols
            ):
                print(
                    f"{new_symbol} IS NOT in symbols - adding to symbol table and deleting symbol {k}"
                )
                # Do we want to keep the original? (numpy.__init__.getVersions)
                symbol_info = package_symbols.pop(k)
                symbol_info["data"]["shadows"] = dereference_relative_import(
                    new_symbol, symbol_info["data"]
                )
                package_symbols[new_symbol] = symbol_info
            else:
                print(
                    f"{new_symbol} IS in symbols so it is also module - deleting '{k}' - keeping module which contains more information"
                )
                del package_symbols[k]


class DirectorySymbolFinder:
    def __init__(self, directory_name: Union[str, Path], parent: str = None):
        self._directory = Path(directory_name)
        self._is_package = is_package(self._directory)
        self._module_path = (
            f"{parent}.{self._directory.name}" if parent else self._directory.name
        )

    def extract_symbols(self) -> dict:
        package_symbols = self._get_all_symbols_in_package()
        remove_shadowed_relative_imports(package_symbols)
        return package_symbols

    def _get_all_symbols_in_package(self) -> dict:
        # TODO: Next line can be parallelized since all files are separate modules
        symbols = [
            parse(module, self._module_path) for module in self._directory.glob("*.py")
        ]
        merged = merge_dicts(*symbols)
        if self._is_package:
            sub_dirs = (d for d in self._directory.iterdir() if d.is_dir())
            for sub_dir in sub_dirs:
                dsf = DirectorySymbolFinder(sub_dir, parent=self._module_path)
                sub_symbols = dsf._get_all_symbols_in_package()
                merged = merge_dicts(merged, sub_symbols)
            return merged
        else:
            return merge_dicts(*symbols)


expected = {
    "numpy.version": {"type": "module", "data": {}},
    "numpy.version.get_versions": {"type": "function", "data": {"lineno": 1}},
    "numpy.__init__": {"type": "module", "data": {}},
    # "numpy.__init__.version": {
    #     "type": "relative-import",
    #     "data": {"shadows": "version", "level": 1},
    # },
    # "numpy.__init__.get_versions": {
    #     "type": "relative-import",
    #     "data": {
    #         "shadows": "version.get_versions",
    #         "level": 1
    #     }
    # },
    # "numpy.__init__.core": {
    #     "type": "relative-import",
    #     "data": {"shadows": "core", "level": 1},
    # },
    "numpy.__init__.relative.*": {
        "type": "relative-star-import",
        "data": {
            "imports": [{"symbol": "core", "level": 1, "module": "numpy.__init__"}]
        },
    },
    "numpy.core.__init__": {"type": "module", "data": {}},
    # "numpy.core.__init__.numeric": {
    #     "type": "relative-import",
    #     "data": {"shadows": "numeric", "level": 1},
    # },
    "numpy.core.__init__.relative.*": {
        "type": "relative-star-import",
        "data": {
            "imports": [
                {"symbol": "numeric", "level": 1, "module": "numpy.core.__init__"}
            ]
        },
    },
    # "numpy.core.__init__.abs": {
    #     "type": "import",
    #     "data": {"shadows": "numeric.absolute"},
    # },
    # "numpy.core.__init__.version": {
    #     "type": "relative-import",
    #     "data": {"shadows": "version", "level": 2},
    # },
    "numpy.core.numeric": {"type": "module", "data": {}},
    "numpy.core.numeric.ones": {"type": "function", "data": {"lineno": 1}},
    "numpy.core.numeric.absolute": {
        "type": "function",
        "data": {"lineno": 5, "symbols_in_volume": {"abs": {"line number": [6]}}},
    },
    "numpy.get_versions": {
        "type": "relative-import",
        "data": {"shadows": "numpy.version.get_versions", "level": 1},
    },
    "numpy.core.version": {
        "type": "relative-import",
        "data": {"shadows": "numpy.version", "level": 2},
    },
    "numpy.core.abs": {
        "type": "relative-import",
        "data": {"shadows": "numpy.core.numeric.absolute", "level": 1},
    },
    "numpy.core.get_versions": {
        "type": "relative-import",
        "data": {"shadows": "numpy.version.get_versions", "level": 2},
    },
    "numpy.core.alias_get_versions": {
        "type": "relative-import",
        "data": {"shadows": "numpy.version.get_versions", "level": 2},
    },
    "numpy.core.alias_version": {
        "type": "relative-import",
        "data": {"shadows": "numpy.version", "level": 2},
    },
}

if __name__ == "__main__":
    import argparse
    import json
    import sys
    from pprint import pprint

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    pprint(args.filename)
    dsf = DirectorySymbolFinder(args.filename)
    symbols = dsf.extract_symbols()
    json.dump(symbols, sys.stdout, indent=2)
    assert symbols == expected

# TODO:
#  - handle relative imports in modules. i.e. not in __init__.py
#  - post process relative star imports
#  - handle aliased relative imports.
#     they are handled but the type from symbol extractor is "import" and not "relative-import"
#     This will be a problem if relative import has more than 1 dot.
#
