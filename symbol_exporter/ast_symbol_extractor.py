import ast
from typing import Any


class SymbolFinder(ast.NodeVisitor):
    def __init__(self, module_name=None):
        if module_name:
            self.current_symbol_stack = [module_name]
            self.symbols = {
                module_name: {
                    "type": "module",
                    "lineno": None,
                    "symbols_in_volume": set(),
                }
            }
        else:
            self.current_symbol_stack = []
            self.symbols = {}
        self.imported_symbols = []
        self.attr_stack = []
        self.used_symbols = set()
        self.aliases = {}

    def visit(self, node: ast.AST) -> Any:
        super().visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        self.imported_symbols.extend(k.name for k in node.names)
        self._recurse_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module and node.level == 0:
            for k in node.names:
                module_name = f"{node.module}.{k.name}"
                self.aliases[k.name] = module_name
                self.imported_symbols.append(module_name)
        self._recurse_visit(node)

    def visit_alias(self, node: ast.alias) -> Any:
        if node.asname:
            self.aliases[node.asname] = self.aliases.get(node.name, node.name)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        self.attr_stack.append(node.attr)
        self._recurse_visit(node)
        self.attr_stack.pop(-1)

    def visit_Assign(self, node: ast.Assign) -> Any:
        # TODO: handle multiple assignments
        # TODO: handle inside class
        # TODO: handle self?
        if len(node.targets) == 1 and len(self.current_symbol_stack) == 0:
            for target in node.targets:
                if hasattr(target, "id"):
                    self.current_symbol_stack.append(target.id)
                    self.symbols[target.id] = {
                        "type": "constant",
                        "lineno": node.lineno,
                        "symbols_in_volume": set(),
                    }
            self._recurse_visit(node)
            self.current_symbol_stack.pop(-1)
        else:
            self._recurse_visit(node)

    def _symbol_stack_to_symbol_name(self):
        return ".".join(self.current_symbol_stack)

    def visit_Call(self, node: ast.Call) -> Any:
        tmp_stack = self.attr_stack.copy()
        self.attr_stack.clear()
        self._recurse_visit(node)
        self.attr_stack = tmp_stack

    def _recurse_visit(self, node):
        for k in ast.iter_child_nodes(node):
            self.visit(k)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.current_symbol_stack.append(node.name)
        self.symbols[self._symbol_stack_to_symbol_name()] = {
            "type": "function",
            "lineno": node.lineno,
            "symbols_in_volume": set(),
        }
        self._recurse_visit(node)
        self.current_symbol_stack.pop(-1)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.current_symbol_stack.append(node.name)
        self.symbols[self._symbol_stack_to_symbol_name()] = {
            "type": "class",
            "lineno": node.lineno,
            "symbols_in_volume": set(),
        }
        # self.aliases["self"] = node.name
        self._recurse_visit(node)
        self.current_symbol_stack.pop(-1)
        # self.aliases.pop("self")

    def visit_Name(self, node: ast.Name) -> Any:
        name = self.aliases.get(node.id, node.id)
        if name in self.imported_symbols:
            symbol_name = ".".join([name] + list(reversed(self.attr_stack)))
            self.used_symbols.add(symbol_name)
            self.symbols[self._symbol_stack_to_symbol_name()]["symbols_in_volume"].add(
                symbol_name
            )
        self._recurse_visit(node)


# 1. get all the imports and their aliases (which includes imported things)
# 2. walk the ast find all usages of those aliases and log all the names and attributes used
# 3. trim those down to symbols (not class attributes)

# TODO: need to handle multiple assignment aliasing
#  Track which data is in what symbols (eg. a symbol is used inside a function definition) so we can build the web
#  of dependencies
#  Just pull all the assignments, aliases, functions and classes and then we don't need jedi (maybe) this would cause
#  us to not handle star imports, which need to be handled specially since their results are version dependant
