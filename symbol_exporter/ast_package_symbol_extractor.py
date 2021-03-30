import ast
from collections import defaultdict
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Union

from symbol_exporter.ast_symbol_extractor import (
    SymbolFinder,
    is_relative_import,
    SymbolType,
    is_relative_star_import,
)


# Move this to ast_symbol_extractor module
def is_star_import(symbol) -> bool:
    return symbol["type"] == SymbolType.STAR_IMPORT


def get_symbol_type(symbol) -> SymbolType:
    return symbol["type"]


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


def normalize_and_sort_symbols(package_symbols: dict):
    """Removes __init__.py from symbols and returns dict sorted by symbol type"""
    ret = {}
    topological_sorter = TopologicalSorter()
    relative_star_imports_volume = {}
    namespaces = defaultdict(list)
    for k, v in sorted(package_symbols.items(), key=lambda x: x[1]["type"]):
        new_symbol = k.replace(".__init__", "")
        if is_relative_import(v):
            shadows = dereference_relative_import(**v["data"])
            print("")
            print(f"derefing {k} which is {new_symbol} and shadows {shadows}")
            data = dict(v, data=dict(shadows=shadows))
            ret[new_symbol] = data
            namespace, symbol = new_symbol.rpartition(".")[:3:2]
            print(f"Adding {new_symbol} to namespace {namespace}")
            namespaces[namespace].append(new_symbol)
        elif is_relative_star_import(v):
            imports = [dereference_relative_import(**data) for data in v["data"]["imports"]]
            data = dict(v, data=dict(imports=imports))
            topological_sorter.add(new_symbol, *[f"{imp}.relative.*" for imp in imports])
            relative_star_imports_volume[new_symbol] = data
            namespace, symbol = new_symbol.partition(".relative")[:3:2]
            print(f"Adding {new_symbol} to namespace {namespace}")
            namespaces[namespace].append(new_symbol)
        else:
            ret[new_symbol] = v
            if get_symbol_type(v) not in {SymbolType.PACKAGE, SymbolType.MODULE}:
                namespace = new_symbol.rpartition(".")[0]
                print(f"Adding {new_symbol} to namespace {namespace}")
                namespaces[namespace].append(new_symbol)
            else:
                namespace = new_symbol.rpartition(".")[0]
                print(f"NOT ADDING {new_symbol} to NS {namespace} - Original is {k}")
    for rel_import in topological_sorter.static_order():
        if rel_import in relative_star_imports_volume:
            ret[rel_import] = relative_star_imports_volume[rel_import]
    return ret, namespaces


def dereference_star_imports(package_symbols: dict, namespaces: dict) -> dict:
    ret = dict(package_symbols)
    star_imports = ((k, v) for k, v in package_symbols.items() if is_relative_star_import(v))
    for k, v in star_imports:
        print(f"IN STARIMPORT is {k}=>{v}")
        namespace = k.partition(".relative")[0]
        imports = v["data"]["imports"]
        add_referenced_symbols(imports, namespace, namespaces, package_symbols, ret)
    return ret


def add_referenced_symbols(imports, namespace, namespaces, package_symbols, ret):
    for rel_star_import in imports:
        print(f"LOOKING for {rel_star_import} in {namespaces}")
        symbols_to_import = namespaces[rel_star_import]
        print(f"symbols_to_import is {symbols_to_import} for namespace {namespace}")
        for symbol in symbols_to_import:
            volume = package_symbols[symbol]
            symbol_type = get_symbol_type(volume)
            s: str = symbol.removeprefix(f"{rel_star_import}")
            new_symbol = f"{namespace}{s}"
            print(f"new symbol is {new_symbol}")
            if symbol_type is SymbolType.RELATIVE_IMPORT:
                print(f"found {symbol} and is {symbol_type}")
                dereferenced_shadows = volume["data"]["shadows"]
                if new_symbol not in package_symbols:
                    print(f"adding symbol {new_symbol} shadowing {dereferenced_shadows}")
                    data = dict(
                        type=SymbolType.RELATIVE_IMPORT,
                        data=dict(shadows=dereferenced_shadows),
                    )
                    ret[new_symbol] = data
                else:
                    print(
                        f"found possible circular reference: {new_symbol} is already in surface area of "
                        f"{namespace}, it is also exposed through import of {rel_star_import}.*"
                    )
            elif symbol_type is SymbolType.RELATIVE_STAR_IMPORT:
                print(f"found {symbol} and is {symbol_type}", end=" - ")
                print("TODO: Deref relative star imports.")
                print(f"new rec import volume is {volume}")
                relative_imports = volume["data"]["imports"]
                print(f"will try to import all symbols in {relative_imports}")
                print(f"Will add symbols {[namespaces[imp] for imp in relative_imports]} to {namespace}")
                add_referenced_symbols(relative_imports, namespace, namespaces, package_symbols, ret)
            elif symbol_type is SymbolType.STAR_IMPORT:
                print(f"found {symbol} and is {symbol_type}", end=" - ")
                print(f"Merging star imports into the {new_symbol} star imports set.")
                default_volume = dict(type=SymbolType.STAR_IMPORT, data=dict(imports=set()))
                imports: set = ret.setdefault(new_symbol, default_volume).get("data", {}).get("imports", set())
                inherited_imports = volume["data"]["imports"]
                imports.update(inherited_imports)
            elif symbol_type in {SymbolType.PACKAGE, SymbolType.MODULE}:
                print(f"found {symbol} and is {symbol_type}.")
                if new_symbol in package_symbols:
                    print(f"Doing nothing. {new_symbol} already exists, most likely a package.")
                else:
                    print(f"adding symbol {new_symbol} shadowing {symbol}")
                    data = dict(
                        type=SymbolType.RELATIVE_IMPORT,
                        data=dict(shadows=symbol),
                    )
                    ret[new_symbol] = data
            else:
                print(f"found {symbol} and is {symbol_type}.")
                print(f"adding symbol {new_symbol} shadowing {symbol}")
                data = dict(type=SymbolType.RELATIVE_IMPORT, data=dict(shadows=symbol))
                ret[new_symbol] = data


class DirectorySymbolFinder:
    def __init__(self, directory_name: Union[str, Path], parent: str = None):
        self._directory = Path(directory_name)
        self._is_package = is_package(self._directory)
        self._module_path = f"{parent}.{self._directory.name}" if parent else self._directory.name

    def extract_symbols(self) -> dict:
        package_symbols = self._get_all_symbols_in_package()
        symbols, namespaces = normalize_and_sort_symbols(package_symbols)
        return dereference_star_imports(symbols, namespaces)

    def _get_all_symbols_in_package(self) -> dict:
        symbols = [parse(module, self._module_path) for module in self._directory.glob("*.py")]
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
