import ast

from symbol_exporter.ast_symbol_extractor import SymbolFinder


def test_from_import_attr_access():
    code = """
from abc import xyz

def f():
    return xyz.i
"""
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"xyz": "abc.xyz"}
    assert z.imported_symbols == ["abc.xyz"]
    assert z.used_symbols == {"abc.xyz.i"}
    assert z.symbols == {
        "f": {"lineno": 4, "symbols_in_volume": {"abc.xyz.i"}, "type": "function"}
    }


def test_alias_import():
    code = """
from abc import xyz as l

def f():
    return l.i
"""
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"xyz": "abc.xyz", "l": "abc.xyz"}
    assert z.imported_symbols == ["abc.xyz"]
    assert z.used_symbols == {"abc.xyz.i"}
    assert z.symbols == {
        "f": {"lineno": 4, "symbols_in_volume": {"abc.xyz.i"}, "type": "function"}
    }


def test_calls():
    code = """
import numpy as np

def f():
    return np.ones(np.twos().three)
"""
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones", "numpy.twos"}
    assert z.symbols == {
        "f": {
            "lineno": 4,
            "symbols_in_volume": {"numpy.ones", "numpy.twos"},
            "type": "function",
        }
    }


def test_constant():
    code = """
import numpy as np

z = np.ones(5)
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones"}
    assert z.symbols == {
        "z": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}, "type": "constant"}
    }


def test_class():
    code = """
import numpy as np

class ABC():
    a = np.ones(5)
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones"}
    assert z.symbols == {
        "ABC": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}, "type": "class"}
    }


def test_class_method():
    code = """
import numpy as np

class ABC():
    a = np.ones(5)

    def xyz(self):
        return np.twos(10)
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones", "numpy.twos"}
    assert z.symbols == {
        "ABC": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}, "type": "class"},
        "ABC.xyz": {
            "lineno": 7,
            "symbols_in_volume": {"numpy.twos"},
            "type": "function",
        },
    }


def test_star_import():
    code = """
import numpy as np
from abc import *
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert not z.used_symbols
    assert z.star_imports == {"abc"}
    assert not z.symbols


def test_undeclared_symbols():
    code = """
import numpy as np

from abc import *
from xyz import *


a = np.ones(5)
b = twos(10)
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones", "twos"}
    assert z.undeclared_symbols == {"twos"}
    assert z.star_imports == {"abc", "xyz"}
    assert z.symbols == {
        "a": {
            "lineno": 8,
            "symbols_in_volume": {"numpy.ones"},
            "type": "constant"},
        "b": {
            "lineno": 9,
            "symbols_in_volume": {"twos"},
            "type": "constant"},
    }


def test_imported_symbols_not_treated_as_undeclared():
    code = """
from abc import twos

b = twos(10)
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"abc.twos"}
    assert z.symbols == {
        "b": {"lineno": 4, "symbols_in_volume": {"abc.twos"}, "type": "constant"}
    }
    assert not z.undeclared_symbols


def test_builtin_symbols_not_treated_as_undeclared():
    code = """
from abc import twos

b = len([])
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"len"}
    assert z.used_builtins == {"len"}
    assert z.symbols == {
        "b": {"lineno": 4, "symbols_in_volume": {"len"}, "type": "constant"}
    }
    assert not z.undeclared_symbols


def test_functions_not_treated_as_undeclared():
    code = """
from abc import twos

def f():
    return 1
    
g = f()
    """
    tree = ast.parse(code)
    z = SymbolFinder()
    z.visit(tree)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"f"}
    assert not z.used_builtins
    assert z.symbols == {
        "f": {"lineno": 4, "symbols_in_volume": set(), "type": "function"},
        'g': {'lineno': 7, 'symbols_in_volume': {'f'}, 'type': 'constant'}
    }
    assert not z.undeclared_symbols
