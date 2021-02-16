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
        "mm": {
            "type": "module",
            "data": {},
        },
        "mm.xyz": {
            "type": "import",
            "data": {"shadows": "abc.xyz"},
        },
        "mm.f": {
            "type": "function",
            "data": {"lineno": 4, "symbols_in_volume": {"abc.xyz.i"}},
        },
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
        "mm": {
            "type": "module",
            "data": {},
        },
        "mm.l": {
            "type": "import",
            "data": {"shadows": "abc.xyz"},
        },
        "mm.f": {
            "type": "function",
            "data": {"lineno": 4, "symbols_in_volume": {"abc.xyz.i"}},
        },
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
        "mm": {
            "type": "module",
            "data": {},
        },
        "mm.f": {
            "type": "function",
            "data": {"lineno": 5, "symbols_in_volume": {"abc.xyz.i"}},
        },
        "mm.xyz": {
            "type": "import",
            "data": {"shadows": "abc.xyz"},
        },
        "mm.l": {
            "type": "import",
            "data": {"shadows": "abc.xyz"},
        },
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
        "mm": {
            "type": "module",
            "data": {},
        },
        "mm.f": {
            "type": "function",
            "data": {"lineno": 4, "symbols_in_volume": {"numpy.ones", "numpy.twos"}},
        },
        "mm.np": {
            "type": "import",
            "data": {"shadows": "numpy"},
        },
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
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"numpy.ones"}},
        },
        "mm.np": {
            "type": "import",
            "data": {"shadows": "numpy"},
        },
        "mm.z": {
            "type": "constant",
            "data": {"lineno": 4},
        },
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
        "mm": {
            "type": "module",
            "data": {},
        },
        "mm.np": {
            "type": "import",
            "data": {"shadows": "numpy"},
        },
        "mm.ABC": {
            "type": "class",
            "data": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}},
        },
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
        "mm": {
            "type": "module",
            "data": {},
        },
        "mm.ABC": {
            "type": "class",
            "data": {"lineno": 4, "symbols_in_volume": {"numpy.ones"}},
        },
        "mm.ABC.xyz": {
            "type": "function",
            "data": {
                "lineno": 7,
                "symbols_in_volume": {"numpy.twos"},
            },
        },
        "mm.np": {
            "type": "import",
            "data": {"shadows": "numpy"},
        },
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
        "mm.np": {
            "type": "import",
            "data": {"shadows": "numpy"},
        },
        "mm.l": {
            "type": "import",
            "data": {"shadows": "abc.xyz"},
        },
        "mm.efg": {
            "type": "import",
            "data": {"shadows": "ggg.efg"},
        },
        "mm.ghi": {
            "type": "import",
            "data": {"shadows": "ghi"},
        },
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"numpy.ones"}},
        },
        "mm.z": {
            "type": "constant",
            "data": {"lineno": 7},
        },
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
    assert z.symbols == {
        "*": {
            "type": "star-import",
            "data": {"imports": {"abc"}},
        },
        "mm.np": {
            "type": "import",
            "data": {"shadows": "numpy"},
        },
        "mm": {
            "type": "module",
            "data": {},
        },
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
    assert z.symbols == {
        "*": {
            "type": "star-import",
            "data": {"imports": {"abc", "xyz"}},
        },
        "mm": {
            "type": "module",
            "data": {
                "symbols_in_volume": {"numpy.ones", "twos"},
            },
        },
        "mm.a": {
            "type": "constant",
            "data": {"lineno": 8},
        },
        "mm.b": {
            "type": "constant",
            "data": {"lineno": 9},
        },
        "mm.np": {
            "type": "import",
            "data": {"shadows": "numpy"},
        },
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
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"abc.twos"}},
        },
        "mm.twos": {
            "type": "import",
            "data": {"shadows": "abc.twos"},
        },
        "mm.b": {
            "type": "constant",
            "data": {"lineno": 4},
        },
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
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"len"}},
        },
        "mm.twos": {
            "type": "import",
            "data": {"shadows": "abc.twos"},
        },
        "mm.b": {
            "type": "constant",
            "data": {"lineno": 4},
        },
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
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"mm.f"}},
        },
        "mm.f": {
            "type": "function",
            "data": {"lineno": 4},
        },
        "mm.twos": {
            "type": "import",
            "data": {"shadows": "abc.twos"},
        },
        "mm.g": {
            "type": "constant",
            "data": {"lineno": 7},
        },
    }
    assert not z.undeclared_symbols
