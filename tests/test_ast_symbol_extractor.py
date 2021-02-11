import ast
from textwrap import dedent

import pytest

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


@pytest.mark.xfail()
def test_import_adds_symbols():
    # np should be a symbol in the surface area since it could be
    # imported from this code issue #23
    code = """
    import numpy as np
    from abc import xyz as l
    from abc import xyz
    
    z = np.ones(5)
    """
    tree = ast.parse(dedent(code))
    z = SymbolFinder()
    z.visit(tree)
    # TODO: should we add a key in the metadata to say that a symbol is
    #  a reference to another symbol?
    assert z.symbols == {
        "np": {},
        "xyz": {},
        "l": {},
        "z": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}, "type": "constant"},
    }
