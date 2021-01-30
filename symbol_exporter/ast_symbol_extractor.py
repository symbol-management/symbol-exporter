import ast
from typing import Any

# Increment when we need the database to be rebuilt (eg adding a new feature)
version = "0"


class SymbolFinder(ast.NodeVisitor):
    def __init__(self):
        self.imported_symbols = []
        self.attr_stack = []
        self.used_symbols = set()
        self.aliases = {}

    def visit(self, node: ast.AST) -> Any:
        super().visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        self.imported_symbols.extend(k.name for k in node.names)
        self.recurse_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module and node.level == 0:
            for k in node.names:
                module_name = f"{node.module}.{k.name}"
                self.aliases[k.name] = module_name
                self.imported_symbols.append(module_name)
        self.recurse_visit(node)

    def visit_alias(self, node: ast.alias) -> Any:
        if node.asname:
            self.aliases[node.asname] = node.name

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        self.attr_stack.append(node.attr)
        self.recurse_visit(node)
        self.attr_stack.pop(-1)

    def visit_Call(self, node: ast.Call) -> Any:
        tmp_stack = self.attr_stack.copy()
        self.attr_stack.clear()
        self.recurse_visit(node)
        self.attr_stack = tmp_stack

    def recurse_visit(self, node):
        for k in ast.iter_child_nodes(node):
            self.visit(k)

    def visit_Name(self, node: ast.Name) -> Any:
        name = self.aliases.get(node.id, node.id)
        while name in self.aliases:
            name = self.aliases.get(name, node.id)
        if name in self.imported_symbols:
            self.used_symbols.add(".".join([name] + list(reversed(self.attr_stack))))
        self.recurse_visit(node)


# 1. get all the imports and their aliases (which includes imported things)
# 2. walk the ast find all usages of those aliases and log all the names and attributes used
# 3. trim those down to symbols (not class attributes)

# TODO: need to handle multiple assignment aliasing
#  Track which data is in what symbols (eg. a symbol is used inside a function definition) so we can build the web
#  of dependencies
#  Just pull all the assignments, aliases, functions and classes and then we don't need jedi (maybe) this would cause
#  us to not handle star imports, which need to be handled specially since their results are version dependant
