import ast
from collections import defaultdict
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Union

from symbol_exporter.ast_symbol_extractor import (
    SymbolFinder,
    is_relative_import,
    SymbolType,
    is_relative_star_import, RELATIVE_IMPORT_IDENTIFIER,
)


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


def resolve_relative_import(module: str, level: int, shadows: str) -> str:
    """Expects data of a relative import"""
    parent = module.split(".")[:-level]
    return ".".join([*parent, shadows])


class _RelativeImportsResolver:
    def __init__(self, symbols):
        self._original_symbols = symbols
        self._sorted_symbols = {}
        self._namespaces = {}

    def resolve(self) -> dict:
        self._normalize_and_sort_symbols()
        return self._resolve_star_imports()

    def _normalize_and_sort_symbols(self):
        """Removes __init__.py from symbols and returns dict sorted by symbol type"""
        tmp_sorted = {}
        topological_sorter = TopologicalSorter()
        relative_star_imports_volume = {}
        namespaces = defaultdict(list)
        for k, v in sorted(self._original_symbols.items(), key=lambda x: x[1]["type"]):
            new_symbol = k.replace(".__init__", "")
            if is_relative_import(v):
                shadows = resolve_relative_import(**v["data"])
                data = dict(v, data=dict(shadows=shadows))
                tmp_sorted[new_symbol] = data
                namespace, _, symbol = new_symbol.rpartition(".")
                namespaces[namespace].append(new_symbol)
            elif is_relative_star_import(v):
                imports = [resolve_relative_import(**data) for data in v["data"]["imports"]]
                data = dict(v, data=dict(imports=imports))
                topological_sorter.add(new_symbol, *[f"{imp}.{RELATIVE_IMPORT_IDENTIFIER}.*" for imp in imports])
                relative_star_imports_volume[new_symbol] = data
                namespace, _, symbol = new_symbol.partition(f".{RELATIVE_IMPORT_IDENTIFIER}")
                namespaces[namespace].append(new_symbol)
            else:
                tmp_sorted[new_symbol] = v
                if get_symbol_type(v) not in {SymbolType.PACKAGE, SymbolType.MODULE}:
                    namespace = new_symbol.rpartition(".")[0]
                    namespaces[namespace].append(new_symbol)
        for rel_import in topological_sorter.static_order():
            if rel_import in relative_star_imports_volume:
                tmp_sorted[rel_import] = relative_star_imports_volume[rel_import]
        self._sorted_symbols = tmp_sorted
        self._namespaces = namespaces

    def _resolve_star_imports(self):
        resolved_symbols = {}
        star_imports = [(k, v) for k, v in self._sorted_symbols.items() if is_relative_star_import(v)]
        if not star_imports:
            return self._sorted_symbols
        else:
            for symbol, volume in star_imports:
                namespace = symbol.partition(f".{RELATIVE_IMPORT_IDENTIFIER}")[0]
                imports = volume["data"]["imports"]
                resolved_symbols |= self._add_referenced_symbols(imports, namespace)
            return resolved_symbols

    def _add_referenced_symbols(self, imports, namespace, symbols=None):
        symbols = dict(self._sorted_symbols) if not symbols else symbols
        for rel_star_import in imports:
            symbols_to_import = self._namespaces[rel_star_import]
            for symbol in symbols_to_import:
                volume = symbols[symbol]
                symbol_type = get_symbol_type(volume)
                s: str = symbol.removeprefix(f"{rel_star_import}")
                new_symbol = f"{namespace}{s}"
                if symbol_type is SymbolType.RELATIVE_IMPORT:
                    print(f"found {symbol} and is {symbol_type}")
                    resolved_shadows = volume["data"]["shadows"]
                    if new_symbol not in symbols:
                        print(f"adding symbol {new_symbol} shadowing {resolved_shadows}")
                        data = dict(type=SymbolType.RELATIVE_IMPORT, data=dict(shadows=resolved_shadows))
                        symbols[new_symbol] = data
                    else:
                        print(f"Doing nothing. {new_symbol} is already in surface area of {namespace}")
                elif symbol_type is SymbolType.RELATIVE_STAR_IMPORT:
                    print(f"found {symbol} and is {symbol_type}")
                    relative_imports = volume["data"]["imports"]
                    print(f"will add all symbols in {relative_imports} to {namespace} namespace")
                    symbols |= self._add_referenced_symbols(relative_imports, namespace, symbols=symbols)
                elif symbol_type is SymbolType.STAR_IMPORT:
                    print(f"found {symbol} and is {symbol_type}", end=" - ")
                    print(f"Merging star imports into the {new_symbol} star imports set.")
                    default_volume = dict(type=SymbolType.STAR_IMPORT, data=dict(imports=set()))
                    imports: set = symbols.setdefault(new_symbol, default_volume).get("data", {}).get("imports", set())
                    inherited_imports = volume["data"]["imports"]
                    imports.update(inherited_imports)
                elif symbol_type in {SymbolType.PACKAGE, SymbolType.MODULE}:
                    print(f"found {symbol} and is {symbol_type}.")
                    if new_symbol in symbols:
                        print(f"Doing nothing. {new_symbol} already exists, most likely a package.")
                    else:
                        print(f"adding symbol {new_symbol} shadowing {symbol}")
                        data = dict(type=SymbolType.RELATIVE_IMPORT, data=dict(shadows=symbol))
                        symbols[new_symbol] = data
                else:
                    print(f"found {symbol} and is {symbol_type}.")
                    print(f"adding symbol {new_symbol} shadowing {symbol}")
                    data = dict(type=SymbolType.RELATIVE_IMPORT, data=dict(shadows=symbol))
                    symbols[new_symbol] = data
        return symbols


class DirectorySymbolFinder:
    def __init__(self, directory_name: Union[str, Path], parent: str = None):
        self._directory = Path(directory_name)
        self._is_package = is_package(self._directory)
        self._module_path = f"{parent}.{self._directory.name}" if parent else self._directory.name

    def extract_symbols(self) -> dict:
        package_symbols = self._get_all_symbols_in_package()
        resolver = _RelativeImportsResolver(package_symbols)
        return resolver.resolve()

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
