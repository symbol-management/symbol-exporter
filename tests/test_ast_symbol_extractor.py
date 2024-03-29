import ast
from textwrap import dedent

from symbol_exporter.ast_symbol_extractor import SymbolFinder, SymbolType


def process_code_str(code, module_name="mm"):
    tree = ast.parse(dedent(code))
    z = SymbolFinder(module_name=module_name)
    z.visit(tree)
    return z


def test_package_name():
    code = """
     from abc import xyz
     """
    z = process_code_str(code, module_name="__init__")
    assert z.symbols == {
        "__init__": {
            "data": {"symbols_in_volume": {"abc.xyz": {"line number": [2]}}},
            "type": SymbolType.PACKAGE,
        },
        "__init__.xyz": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.xyz"},
        },
    }


def test_fully_qualified_package_names():
    code = """
     from abc import xyz
     """
    z = process_code_str(code, module_name="mm.__init__")
    assert z.symbols == {
        "mm.__init__": {
            "data": {"symbols_in_volume": {"abc.xyz": {"line number": [2]}}},
            "type": SymbolType.PACKAGE,
        },
        "mm.__init__.xyz": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.xyz"},
        },
    }


def test_fully_qualified_module_names():
    code = """
     from abc import xyz
     """
    z = process_code_str(code, module_name="mm.core")
    assert z.symbols == {
        "mm.core": {
            "data": {"symbols_in_volume": {"abc.xyz": {"line number": [2]}}},
            "type": SymbolType.MODULE,
        },
        "mm.core.xyz": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.xyz"},
        },
    }


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
            "data": {"symbols_in_volume": {"abc.xyz": {"line number": [2]}}},
            "type": SymbolType.MODULE,
        },
        "mm.xyz": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.xyz"},
        },
        "mm.f": {
            "type": SymbolType.FUNCTION,
            "data": {
                "lineno": 4,
                "symbols_in_volume": {"abc.xyz.i": {"line number": [5]}},
            },
        },
    }


def test_import_in_function():
    code = """
    def f():
        from abc import xyz
        return xyz.i
    """
    z = process_code_str(code)
    assert z.symbols == {
        "mm": {
            "type": SymbolType.MODULE,
            "data": {},
        },
        "mm.f": {
            "type": SymbolType.FUNCTION,
            "data": {
                "lineno": 2,
                "symbols_in_volume": {"abc.xyz.i": {"line number": [4]}, "abc.xyz": {"line number": [3]}},
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
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"abc.xyz": {"line number": [2]}}},
        },
        "mm.l": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.xyz"},
        },
        "mm.f": {
            "type": SymbolType.FUNCTION,
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
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"abc.xyz": {"line number": [2, 3]}}},
        },
        "mm.f": {
            "type": SymbolType.FUNCTION,
            "data": {
                "lineno": 5,
                "symbols_in_volume": {"abc.xyz.i": {"line number": [6]}},
            },
        },
        "mm.xyz": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.xyz"},
        },
        "mm.l": {
            "type": SymbolType.IMPORT,
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
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"numpy": {"line number": [2]}}},
        },
        "mm.f": {
            "type": SymbolType.FUNCTION,
            "data": {
                "lineno": 4,
                "symbols_in_volume": {
                    "numpy.ones": {"line number": [5]},
                    "numpy.twos": {"line number": [5]},
                },
            },
        },
        "mm.np": {
            "type": SymbolType.IMPORT,
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
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"numpy.ones": {"line number": [4]}, "numpy": {"line number": [2]}}},
        },
        "mm.np": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "numpy"},
        },
        "mm.z": {
            "type": SymbolType.CONSTANT,
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
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"numpy": {"line number": [2]}}},
        },
        "mm.np": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "numpy"},
        },
        "mm.ABC": {
            "type": SymbolType.CLASS,
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
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"numpy": {"line number": [2]}}},
        },
        "mm.ABC": {
            "type": SymbolType.CLASS,
            "data": {
                "lineno": 4,
                "symbols_in_volume": {"numpy.ones": {"line number": [5]}},
            },
        },
        "mm.ABC.xyz": {
            "type": SymbolType.FUNCTION,
            "data": {
                "lineno": 7,
                "symbols_in_volume": {"numpy.twos": {"line number": [8]}},
            },
        },
        "mm.np": {
            "type": SymbolType.IMPORT,
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
            "type": SymbolType.IMPORT,
            "data": {"shadows": "numpy"},
        },
        "mm.l": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.xyz"},
        },
        "mm.efg": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "ggg.efg"},
        },
        "mm.ghi": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "ghi"},
        },
        "mm": {
            "data": {
                "symbols_in_volume": {
                    "abc.xyz": {"line number": [3]},
                    "ggg.efg": {"line number": [4]},
                    "ghi": {"line number": [5]},
                    "numpy": {"line number": [2]},
                    "numpy.ones": {"line number": [7]},
                }
            },
            "type": SymbolType.MODULE,
        },
        "mm.z": {
            "type": SymbolType.CONSTANT,
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
        "mm.*": {
            "type": SymbolType.STAR_IMPORT,
            "data": {"imports": {"abc"}},
        },
        "mm.np": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "numpy"},
        },
        "mm": {
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"abc": {"line number": [3]}, "numpy": {"line number": [2]}}},
        },
    }


def test_relative_import():
    code = """
    from . import core
    from .core import ones
    from ..core import twos
    """
    z = process_code_str(code)
    assert z.symbols == {
        "mm.core": {
            "type": SymbolType.RELATIVE_IMPORT,
            "data": {"shadows": "core", "level": 1, "module": "mm"},
        },
        "mm.ones": {
            "type": SymbolType.RELATIVE_IMPORT,
            "data": {"shadows": "core.ones", "level": 1, "module": "mm"},
        },
        "mm.twos": {
            "type": SymbolType.RELATIVE_IMPORT,
            "data": {"shadows": "core.twos", "level": 2, "module": "mm"},
        },
        "mm": {
            "type": SymbolType.MODULE,
            "data": {},
        },
    }


def test_relative_alias_import():
    code = """
    from . import core as c
    from .core import ones as c_ones
    from ..core import twos as c_twos
    """
    z = process_code_str(code)
    assert z.symbols == {
        "mm": {"data": {}, "type": SymbolType.MODULE},
        "mm.c": {
            "type": SymbolType.RELATIVE_IMPORT,
            "data": {"shadows": "core", "level": 1, "module": "mm"},
        },
        "mm.c_ones": {
            "type": SymbolType.RELATIVE_IMPORT,
            "data": {"shadows": "core.ones", "level": 1, "module": "mm"},
        },
        "mm.c_twos": {
            "type": SymbolType.RELATIVE_IMPORT,
            "data": {"shadows": "core.twos", "level": 2, "module": "mm"},
        },
    }


def test_relative_star_import():
    code = """
    from .core import *
    from ..numeric import *
    """
    z = process_code_str(code)
    assert z.symbols == {
        "mm": {"data": {}, "type": SymbolType.MODULE},
        "mm.~~RELATIVE~~.*": {
            "type": SymbolType.RELATIVE_STAR_IMPORT,
            "data": {
                "imports": [
                    {
                        "shadows": "core",
                        "level": 1,
                        "module": "mm",
                    },
                    {
                        "shadows": "numeric",
                        "level": 2,
                        "module": "mm",
                    },
                ]
            },
        },
    }


def test_bare_relative_star_import():
    code = """
    from . import *
    from .. import *
    """
    z = process_code_str(code)
    assert z.symbols == {
        "mm": {"data": {}, "type": SymbolType.MODULE},
        "mm.~~RELATIVE~~.*": {
            "type": SymbolType.RELATIVE_STAR_IMPORT,
            "data": {
                "imports": [
                    {
                        "shadows": "__init__",
                        "level": 1,
                        "module": "mm",
                    },
                    {
                        "shadows": "__init__",
                        "level": 2,
                        "module": "mm",
                    },
                ]
            },
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
        "mm.*": {
            "type": SymbolType.STAR_IMPORT,
            "data": {"imports": {"abc", "xyz"}},
        },
        "mm": {
            "type": SymbolType.MODULE,
            "data": {
                "symbols_in_volume": {
                    "abc": {"line number": [4]},
                    "numpy": {"line number": [2]},
                    "xyz": {"line number": [5]},
                    "numpy.ones": {"line number": [8]},
                    "twos": {"line number": [9]},
                },
            },
        },
        "mm.a": {
            "type": SymbolType.CONSTANT,
            "data": {"lineno": 8},
        },
        "mm.b": {
            "type": SymbolType.CONSTANT,
            "data": {"lineno": 9},
        },
        "mm.np": {
            "type": SymbolType.IMPORT,
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
            "type": SymbolType.MODULE,
            "data": {"symbols_in_volume": {"abc.twos": {"line number": [2, 4]}}},
        },
        "mm.twos": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.twos"},
        },
        "mm.b": {
            "type": SymbolType.CONSTANT,
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
            "type": SymbolType.MODULE,
            "data": {
                "symbols_in_volume": {"len": {"line number": [4]}, "abc.twos": {"line number": [2]}},
            },
        },
        "mm.twos": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.twos"},
        },
        "mm.b": {
            "type": SymbolType.CONSTANT,
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
            "type": SymbolType.MODULE,
            "data": {
                "symbols_in_volume": {"mm.f": {"line number": [7]}, "abc.twos": {"line number": [2]}},
            },
        },
        "mm.f": {
            "type": SymbolType.FUNCTION,
            "data": {"lineno": 4},
        },
        "mm.twos": {
            "type": SymbolType.IMPORT,
            "data": {"shadows": "abc.twos"},
        },
        "mm.g": {
            "type": SymbolType.CONSTANT,
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
                    "abc.twos": {"line number": [2]},
                    "abc.twos.three": {"line number": [4]},
                    "abc.twos.four": {"line number": [5]},
                }
            },
            "type": SymbolType.MODULE,
        },
        "mm.twos": {"data": {"shadows": "abc.twos"}, "type": SymbolType.IMPORT},
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
        "mm": {"data": {}, "type": SymbolType.MODULE},
        "mm.a": {
            "data": {"lineno": 2, "symbols_in_volume": {"mm.b": {"line number": [3]}}},
            "type": SymbolType.FUNCTION,
        },
        "mm.b": {"data": {"lineno": 5}, "type": SymbolType.FUNCTION},
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
        "mm": {"data": {}, "type": SymbolType.MODULE},
        "mm.a": {
            "data": {
                "lineno": 2,
                "symbols_in_volume": {"ones": {"line number": [3, 4]}},
            },
            "type": SymbolType.FUNCTION,
        },
    }


def test_self_is_callable():
    code = """
    class A:
        def a(self, job_name_class=None):
            self()
        def b(self):
            self.z = self.x
    """
    z = process_code_str(code)
    assert z.undeclared_symbols == set()
    assert z.post_process_symbols() == {
        "mm": {"data": {}, "type": SymbolType.MODULE},
        "mm.A": {"data": {"lineno": 2}, "type": SymbolType.CLASS},
        "mm.A.a": {"data": {"lineno": 3}, "type": SymbolType.FUNCTION},
        "mm.A.b": {"data": {"lineno": 5}, "type": SymbolType.FUNCTION},
    }


def test_symbols_in_volume_names():
    code = """
    import ast

    z = [ast.Try]
    z.sort()
    """
    z = process_code_str(code)
    assert z.undeclared_symbols == set()
    assert z.post_process_symbols() == {
        "mm": {
            "data": {
                "symbols_in_volume": {
                    "ast.Try": {"line number": [4]},
                    "ast": {"line number": [2]},
                    "mm.z": {"line number": [5]},
                }
            },
            "type": SymbolType.MODULE,
        },
        "mm.ast": {"data": {"shadows": "ast"}, "type": SymbolType.IMPORT},
        "mm.z": {"data": {"lineno": 4}, "type": SymbolType.CONSTANT},
    }
