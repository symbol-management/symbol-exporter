import ast
import builtins
from typing import Any
from enum import Enum

# Increment when we need the database to be rebuilt (eg adding a new feature)
version = "1.2"
builtin_symbols = set(dir(builtins))


class SymbolType(str, Enum):
    MODULE = "module"
    IMPORT = "import"
    FUNCTION = "function"
    CONSTANT = "constant"
    CLASS = "class"
    STAR_IMPORT = "star-import"


class SymbolFinder(ast.NodeVisitor):
    def __init__(self, module_name):
        self._module_name = module_name
        self.current_symbol_stack = [module_name]
        self._symbols = {
            module_name: {
                "type": SymbolType.MODULE,
                "data": {},
            }
        }
        self.imported_symbols = []
        self.attr_stack = []
        self.used_symbols = set()
        self.aliases = {}
        self.undeclared_symbols = set()
        self.used_builtins = set()

    @property
    def symbols(self):
        return self.post_process_symbols()

    def visit(self, node: ast.AST) -> Any:
        super().visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        self.imported_symbols.extend(k.name for k in node.names)
        for k in node.names:
            if not k.asname:
                self._add_symbol_to_surface_area(
                    SymbolType.IMPORT, symbol=k.name, shadows=k.name
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module and node.level == 0:
            for k in node.names:
                if k.name != "*":
                    module_name = f"{node.module}.{k.name}"
                    self.aliases[k.name] = module_name
                    self.imported_symbols.append(module_name)
                    if not k.asname:
                        self._add_symbol_to_surface_area(
                            SymbolType.IMPORT, symbol=k.name, shadows=module_name
                        )
                else:
                    self._add_symbol_to_star_imports(node.module)
        self.generic_visit(node)

    def visit_alias(self, node: ast.alias) -> Any:
        if node.asname:
            alias_name = self.aliases.get(node.name, node.name)
            self.aliases[node.asname] = alias_name
            self._add_symbol_to_surface_area(
                SymbolType.IMPORT, symbol=node.asname, shadows=alias_name
            )

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        self.attr_stack.append(node.attr)
        self.generic_visit(node)
        self.attr_stack.pop(-1)

    def visit_Assign(self, node: ast.Assign) -> Any:
        # TODO: handle multiple assignments
        # TODO: handle inside class
        # TODO: handle self?
        if len(node.targets) == 1 and len(self.current_symbol_stack) == 1:
            target = next(iter(node.targets))
            if hasattr(target, "id"):
                self.current_symbol_stack.append(target.id)
                symbol_name = self._symbol_stack_to_symbol_name()
                self._add_symbol_to_surface_area(
                    SymbolType.CONSTANT,
                    symbol_name,
                    lineno=node.lineno,
                )
            self.generic_visit(node)
            if hasattr(target, "id"):
                self.current_symbol_stack.pop(-1)
        else:
            self.generic_visit(node)

    def _symbol_stack_to_symbol_name(self):
        return ".".join(self.current_symbol_stack)

    def visit_Call(self, node: ast.Call) -> Any:
        if (
            hasattr(node.func, "id")
            and node.func.id not in self.aliases
            and node.func.id not in builtin_symbols
            and not self._symbol_in_surface_area(node.func.id)
        ):
            self.undeclared_symbols.add(node.func.id)
        tmp_stack = self.attr_stack.copy()
        self.attr_stack.clear()
        self.generic_visit(node)
        self.attr_stack = tmp_stack

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.current_symbol_stack.append(node.name)
        symbol_name = self._symbol_stack_to_symbol_name()
        self._add_symbol_to_surface_area(
            SymbolType.FUNCTION,
            symbol_name,
            lineno=node.lineno,
        )
        self.generic_visit(node)
        self.current_symbol_stack.pop(-1)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.current_symbol_stack.append(node.name)
        symbol_name = self._symbol_stack_to_symbol_name()
        self._add_symbol_to_surface_area(
            SymbolType.CLASS, symbol_name, lineno=node.lineno
        )
        # self.aliases["self"] = node.name
        self.generic_visit(node)
        self.current_symbol_stack.pop(-1)
        # self.aliases.pop("self")

    def visit_Name(self, node: ast.Name) -> Any:
        def get_symbol_name(name):
            return self._symbol_in_surface_area(name) or ".".join(
                [name] + list(reversed(self.attr_stack))
            )

        name = self.aliases.get(node.id, node.id)
        if name in builtin_symbols:
            self.used_builtins.add(name)
        if self._symbol_previously_seen(name):
            symbol_name = get_symbol_name(name)
            if not self._is_constant(symbol_name):
                self.used_symbols.add(symbol_name)
            # Do not add myself to my own volume.
            # A previously declared symbol in the module is being referenced.
            surface_symbol = self._symbol_stack_to_symbol_name()
            if symbol_name != surface_symbol:
                if self._is_constant(surface_symbol):
                    self._add_symbol_to_volume(
                        surface_symbol=self._module_name, volume_symbol=symbol_name
                    )
                else:
                    self._add_symbol_to_volume(
                        surface_symbol=surface_symbol, volume_symbol=symbol_name
                    )
        self.generic_visit(node)

    def _is_constant(self, symbol_name):
        return self._symbols.get(symbol_name, {}).get("type") == SymbolType.CONSTANT

    def _symbol_previously_seen(self, symbol):
        return (
            symbol in self.imported_symbols
            or symbol in self.undeclared_symbols
            or symbol in builtin_symbols
            or self._symbol_in_surface_area(symbol)
        )

    def _symbol_in_surface_area(self, symbol):
        fully_qualified_symbol_name = f"{self._module_name}.{symbol}"
        if fully_qualified_symbol_name in self._symbols:
            return fully_qualified_symbol_name
        else:
            return None

    def _add_symbol_to_surface_area(self, symbol_type: SymbolType, symbol, **kwargs):
        full_symbol_name = (
            f"{self._module_name}.{symbol}"
            if symbol_type is SymbolType.IMPORT
            else symbol
        )
        self._symbols[full_symbol_name] = dict(type=symbol_type, data=kwargs)

    def _add_symbol_to_volume(self, surface_symbol, volume_symbol):
        data = self._symbols[surface_symbol]["data"]
        data.setdefault("symbols_in_volume", set()).add(volume_symbol)

    def _add_symbol_to_star_imports(self, imported_symbol):
        default = dict(type=SymbolType.STAR_IMPORT, data=dict(imports=set()))
        self._symbols.setdefault("*", default)["data"]["imports"].add(imported_symbol)

    def post_process_symbols(self):
        stripped_names = {
            k.split(f"{self._module_name}.")[1]: k
            for k in self._symbols
            if k != self._module_name and k != "*"
        }
        output_symbols = self._symbols
        for k, v in output_symbols.items():
            volume = v["data"].get("symbols_in_volume")
            if volume:
                for bad_func_name in volume & set(stripped_names):
                    volume.remove(bad_func_name)
                    volume.add(stripped_names[bad_func_name])
                    self.undeclared_symbols.remove(bad_func_name)
        return output_symbols


# 1. get all the imports and their aliases (which includes imported things)
# 2. walk the ast find all usages of those aliases and log all the names and attributes used
# 3. trim those down to symbols (not class attributes)

# TODO: need to handle multiple assignment aliasing
#  Track which data is in what symbols (eg. a symbol is used inside a function definition) so we can build the web
#  of dependencies
#  Just pull all the assignments, aliases, functions and classes and then we don't need jedi (maybe) this would cause
#  us to not handle star imports, which need to be handled specially since their results are version dependant
