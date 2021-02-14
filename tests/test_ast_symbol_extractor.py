import ast
from textwrap import dedent

from symbol_exporter.ast_symbol_extractor import SymbolFinder


def test_from_import_attr_access():
    code = """
from abc import xyz

def f():
    return xyz.i
"""
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"xyz": "abc.xyz"}
    assert z.imported_symbols == ["abc.xyz"]
    assert z.used_symbols == {"abc.xyz.i"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': set(), 'type': 'module'},
        "mm.xyz": {"lineno": None, "shadows": "abc.xyz", "type": "import"},
        "mm.f": {"lineno": 4, "symbols_in_volume": {"abc.xyz.i"}, "type": "function"}
    }


def test_alias_import():
    code = """
from abc import xyz as l

def f():
    return l.i
"""
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"xyz": "abc.xyz", "l": "abc.xyz"}
    assert z.imported_symbols == ["abc.xyz"]
    assert z.used_symbols == {"abc.xyz.i"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': set(), 'type': 'module'},
        "mm.l": {"lineno": None, "type": "import", "shadows": "abc.xyz"},
        "mm.f": {"lineno": 4, "symbols_in_volume": {"abc.xyz.i"}, "type": "function"}
    }


def test_import_with_and_without_alias_exposes_import_and_alias():
    code = """
from abc import xyz
from abc import xyz as l

def f():
    return l.i
"""
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"xyz": "abc.xyz", "l": "abc.xyz"}
    assert z.imported_symbols == ["abc.xyz", "abc.xyz"]
    assert z.used_symbols == {"abc.xyz.i"}
    assert z.symbols == {
        "mm": {"lineno": None, "symbols_in_volume": set(), "type": "module"},
        "mm.f": {"lineno": 5, "symbols_in_volume": {"abc.xyz.i"}, "type": "function"},
        "mm.xyz": {"lineno": None, "type": "import", "shadows": "abc.xyz"},
        "mm.l": {"lineno": None, "type": "import", "shadows": "abc.xyz"}
    }


def test_calls():
    code = """
import numpy as np

def f():
    return np.ones(np.twos().three)
"""
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones", "numpy.twos"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': set(), 'type': 'module'},
        "mm.f": {
            "lineno": 4,
            "symbols_in_volume": {"numpy.ones", "numpy.twos"},
            "type": "function",
        },
        "mm.np": {"shadows": "numpy", "lineno": None, "type": "import"}
    }


def test_constant():
    code = """
import numpy as np

z = np.ones(5)
    """
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': {"numpy.ones"}, 'type': 'module'},
        "mm.np": {"shadows": "numpy", "lineno": None, "type": "import"},
        "mm.z": {"lineno": 4, "symbols_in_volume": set(), "type": "constant"}
    }


def test_class():
    code = """
import numpy as np

class ABC():
    a = np.ones(5)
    """
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': set(), 'type': 'module'},
        "mm.np": {"shadows": "numpy", "lineno": None, "type": "import"},
        "mm.ABC": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}, "type": "class"}
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
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones", "numpy.twos"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': set(), 'type': 'module'},
        "mm.ABC": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}, "type": "class"},
        "mm.ABC.xyz": {
            "lineno": 7,
            "symbols_in_volume": {"numpy.twos"},
            "type": "function",
        },
        "mm.np": {"shadows": "numpy", "lineno": None, "type": "import"}
    }


def test_import_adds_symbols():
    code = """
    import numpy as np
    from abc import xyz as l
    from ggg import efg
    import ghi

    z = np.ones(5)
    """
    tree = ast.parse(dedent(code))
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.symbols == {
        "mm.np": {"shadows": "numpy", "lineno": None, "type": "import"},
        "mm.l": {"shadows": "abc.xyz", "lineno": None, "type": "import"},
        "mm.efg": {"shadows": "ggg.efg", "lineno": None, "type": "import"},
        "mm.ghi": {"shadows": "ghi", "lineno": None, "type": "import"},
        "mm": {"lineno": None, "symbols_in_volume": {"numpy.ones"}, "type": "module"},
        "mm.z": {"lineno": 7, "symbols_in_volume": set(), "type": "constant"},
    }


def test_star_import():
    code = """
import numpy as np
from abc import *
    """
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert not z.used_symbols
    assert z.star_imports == {"abc"}
    assert z.symbols == {
        "mm.np": {"shadows": "numpy", "lineno": None, "type": "import"},
        'mm': {'lineno': None, 'symbols_in_volume': set(), 'type': 'module'}
    }


def test_undeclared_symbols():
    code = """
import numpy as np

from abc import *
from xyz import *


a = np.ones(5)
b = twos(10)
    """
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones", "twos"}
    assert z.undeclared_symbols == {"twos"}
    assert z.star_imports == {"abc", "xyz"}
    assert z.symbols == {
        'mm': {
            'lineno': None,
            'symbols_in_volume': {"numpy.ones", "twos"},
            'type': 'module'},
        "mm.a": {
            "lineno": 8,
            "symbols_in_volume": set(),
            "type": "constant"},
        "mm.b": {
            "lineno": 9,
            "symbols_in_volume": set(),
            "type": "constant"},
        "mm.np": {"shadows": "numpy", "lineno": None, "type": "import"}
    }


def test_imported_symbols_not_treated_as_undeclared():
    code = """
from abc import twos

b = twos(10)
    """
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"abc.twos"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': {"abc.twos"}, 'type': 'module'},
        "mm.twos": {"lineno": None, "shadows": "abc.twos", "type": "import"},
        "mm.b": {"lineno": 4, "symbols_in_volume": set(), "type": "constant"}
    }
    assert not z.undeclared_symbols


def test_builtin_symbols_not_treated_as_undeclared():
    code = """
from abc import twos

b = len([])
    """
    tree = ast.parse(code)
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"len"}
    assert z.used_builtins == {"len"}
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': {"len"}, 'type': 'module'},
        "mm.twos": {"lineno": None, "shadows": "abc.twos", "type": "import"},
        "mm.b": {"lineno": 4, "symbols_in_volume": set(), "type": "constant"}
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
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"mm.f"}
    assert not z.used_builtins
    assert z.symbols == {
        'mm': {'lineno': None, 'symbols_in_volume': {'mm.f'}, 'type': 'module'},
        "mm.f": {"lineno": 4, "symbols_in_volume": set(), "type": "function"},
        "mm.twos": {"lineno": None, "shadows": "abc.twos", "type": "import"},
        'mm.g': {'lineno': 7, 'symbols_in_volume': set(), 'type': 'constant'}
    }
    assert not z.undeclared_symbols
