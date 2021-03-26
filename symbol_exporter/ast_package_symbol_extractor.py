import ast
from pathlib import Path
from typing import Union

from symbol_exporter.ast_symbol_extractor import (
    SymbolFinder,
    is_relative_import,
    SymbolType,
    is_relative_star_import,
)
from symbol_exporter.db_access_model import make_json_friendly


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


def dereference_relative_import(module: str, level: int, shadows: str) -> str:
    """Expects data of a relative import"""
    parent = module.split(".")[:-level]
    return ".".join([*parent, shadows])


def remove_shadowed_relative_imports(package_symbols: dict):
    ret = {}
    for k, v in sorted(package_symbols.items(), key=lambda x: x[1]["type"]):
        new_symbol = k.replace(".__init__", "")
        if is_relative_import(v):
            shadows = dereference_relative_import(**v["data"])
            print(f"derefing {k} which is {new_symbol} and shadows {shadows}")
            data = dict(v, data=dict(shadows=shadows))
            ret[new_symbol] = data
        else:
            ret[new_symbol] = v
    return ret


def deref_star(package_symbols: dict) -> dict:
    ret = {}
    star_imports = (
        (k, v) for k, v in package_symbols.items() if is_relative_star_import(v)
    )
    for k, v in star_imports:
        imports = v["data"]["imports"]
        for rel_import in imports:
            shadows = dereference_relative_import(**rel_import)
            namespace = rel_import["module"].replace(".__init__", "")
            print(f"Looking at symbol {k} with data {v} which shadows: {shadows}")
            for symbol in package_symbols:
                print(f"looking at symbol {symbol}")
                if symbol.startswith(shadows) and package_symbols[symbol][
                    "type"
                ] not in {
                    SymbolType.PACKAGE,
                    SymbolType.MODULE,
                    SymbolType.STAR_IMPORT,
                    SymbolType.RELATIVE_STAR_IMPORT,
                }:
                    print(f"found symbol {symbol} for shadow {shadows}")
                    s: str = symbol.removeprefix(f"{shadows}")
                    new_symbol = f"{namespace}{s}"
                    # print(f"adding {new_symbol} as star imported symbol")
                    print(f"looking for v {package_symbols[symbol]}")
                    if is_relative_import(package_symbols[symbol]):
                        dereferenced_shadows = package_symbols[symbol]["data"][
                            "shadows"
                        ]
                        # print(f"rel import shadows {dereferenced_shadows}")
                        if new_symbol != dereferenced_shadows:
                            # do not add new symbol if same, it is circular reference
                            print(
                                f"adding symbol {new_symbol} shadowing {dereferenced_shadows}"
                            )
                        else:
                            print(
                                f"found circular reference: {new_symbol} is already in volume of "
                                f"{rel_import['module']}, it is also exposed through import {shadows}.*"
                            )
                    else:
                        print(f"adding symbol {new_symbol} shadowing {symbol}")
            data = dict(v, data=dict(shadows=shadows))
            ret[new_symbol] = data
        # ret[new_symbol] = v
    return ret


class DirectorySymbolFinder:
    def __init__(self, directory_name: Union[str, Path], parent: str = None):
        self._directory = Path(directory_name)
        self._is_package = is_package(self._directory)
        self._module_path = (
            f"{parent}.{self._directory.name}" if parent else self._directory.name
        )

    def extract_symbols(self) -> dict:
        package_symbols = self._get_all_symbols_in_package()
        r = remove_shadowed_relative_imports(package_symbols)
        s = deref_star(r)
        return s

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
    "numpy.version": {"type": SymbolType.MODULE, "data": {}},
    "numpy.version.get_versions": {"type": SymbolType.FUNCTION, "data": {"lineno": 4}},
    "numpy": {"type": SymbolType.PACKAGE, "data": {}},
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
    "numpy.relative.*": {
        "type": SymbolType.RELATIVE_STAR_IMPORT,
        "data": {
            "imports": [{"shadows": "core", "level": 1, "module": "numpy.__init__"}]
        },
    },
    "numpy.core": {"type": SymbolType.PACKAGE, "data": {}},
    # "numpy.core.__init__.numeric": {
    #     "type": "relative-import",
    #     "data": {"shadows": "numeric", "level": 1},
    # },
    "numpy.core.relative.*": {
        "type": SymbolType.RELATIVE_STAR_IMPORT,
        "data": {
            "imports": [
                {"shadows": "numeric", "level": 1, "module": "numpy.core.__init__"}
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
    "numpy.core.*": {"type": SymbolType.STAR_IMPORT, "data": {"imports": {"requests"}}},
    "numpy.*": {"type": SymbolType.STAR_IMPORT, "data": {"imports": {"requests"}}},
    "numpy.version.*": {
        "type": SymbolType.STAR_IMPORT,
        "data": {"imports": {"requests"}},
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
    json.dump(symbols, sys.stdout, indent=2, default=make_json_friendly)
    assert symbols == expected

# TODO:
#  - handle relative imports in modules. i.e. not in __init__.py
#  - post process relative star imports
