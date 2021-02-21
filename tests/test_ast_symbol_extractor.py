import ast
from textwrap import dedent

from symbol_exporter.ast_symbol_extractor import SymbolFinder


def process_code_str(code):
    tree = ast.parse(dedent(code))
    z = SymbolFinder(module_name="mm")
    z.visit(tree)
    return z


def test_from_import_attr_access():
    code = """
    from abc import xyz

    def f():
        return xyz.i
    """
    z = process_code_str(code)
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
            "data": {
                "lineno": 4,
                "symbols_in_volume": {"abc.xyz.i": {"line number": [5]}},
            },
        },
    }


def test_alias_import():
    code = """
    from abc import xyz as l

    def f():
        return l.i
    """
    z = process_code_str(code)
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
            "data": {
                "lineno": 4,
                "symbols_in_volume": {"abc.xyz.i": {"line number": [5]}},
            },
        },
    }


def test_import_with_and_without_alias_exposes_import_and_alias():
    code = """
    from abc import xyz
    from abc import xyz as l

    def f():
        return l.i
"""
    z = process_code_str(code)
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
            "data": {
                "lineno": 5,
                "symbols_in_volume": {"abc.xyz.i": {"line number": [6]}},
            },
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
    z = process_code_str(code)
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
            "data": {
                "lineno": 4,
                "symbols_in_volume": {
                    "numpy.ones": {"line number": [5]},
                    "numpy.twos": {"line number": [5]},
                },
            },
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
    z = process_code_str(code)
    assert z.aliases == {"np": "numpy"}
    assert z.imported_symbols == ["numpy"]
    assert z.used_symbols == {"numpy.ones"}
    assert z.symbols == {
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"numpy.ones": {"line number": [4]}}},
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
    z = process_code_str(code)
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
            "data": {
                "lineno": 4,
                "symbols_in_volume": {"numpy.ones": {"line number": [5]}},
            },
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
    z = process_code_str(code)
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
            "data": {
                "lineno": 4,
                "symbols_in_volume": {"numpy.ones": {"line number": [5]}},
            },
        },
        "mm.ABC.xyz": {
            "type": "function",
            "data": {
                "lineno": 7,
                "symbols_in_volume": {"numpy.twos": {"line number": [8]}},
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
    z = process_code_str(code)
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
            "data": {"symbols_in_volume": {"numpy.ones": {"line number": [7]}}},
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
    z = process_code_str(code)
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
    z = process_code_str(code)
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
                "symbols_in_volume": {
                    "numpy.ones": {"line number": [8]},
                    "twos": {"line number": [9]},
                },
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
    z = process_code_str(code)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"abc.twos"}
    assert z.symbols == {
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"abc.twos": {"line number": [4]}}},
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
    z = process_code_str(code)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"len"}
    assert z.used_builtins == {"len"}
    assert z.symbols == {
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"len": {"line number": [4]}}},
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
    z = process_code_str(code)
    assert z.aliases == {"twos": "abc.twos"}
    assert z.imported_symbols == ["abc.twos"]
    assert z.used_symbols == {"mm.f"}
    assert not z.used_builtins
    assert z.symbols == {
        "mm": {
            "type": "module",
            "data": {"symbols_in_volume": {"mm.f": {"line number": [7]}}},
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


def test_attr_assignment():
    code = """
    from abc import twos

    twos.three = '*'
    twos.four = None
    """
    z = process_code_str(code)
    assert z.symbols == {
        "mm": {
            "data": {
                "symbols_in_volume": {
                    "abc.twos.three": {"line number": [4]},
                    "abc.twos.four": {"line number": [5]},
                }
            },
            "type": "module",
        },
        "mm.twos": {"data": {"shadows": "abc.twos"}, "type": "import"},
    }


def test_out_of_order_func_def():
    code = """
    def a():
        return b()

    def b():
        return 1
    """
    z = process_code_str(code)
    assert z.post_process_symbols() == {
        "mm": {"data": {}, "type": "module"},
        "mm.a": {
            "data": {"lineno": 2, "symbols_in_volume": {"mm.b": {"line number": [3]}}},
            "type": "function",
        },
        "mm.b": {"data": {"lineno": 5}, "type": "function"},
    }


def test_multi_use_of_symbol():
    code = """
    def a():
        a = ones(5)
        b = ones(5)
        return a + b
    """
    z = process_code_str(code)
    assert z.post_process_symbols() == {
        "mm": {"data": {}, "type": "module"},
        "mm.a": {
            "data": {
                "lineno": 2,
                "symbols_in_volume": {"ones": {"line number": [3, 4]}},
            },
            "type": "function",
        },
    }
