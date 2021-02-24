from enum import Enum
from dataclasses import dataclass
import re
import struct
from typing import Optional
import logging

import colorlog

ASM_PATTERN = re.compile(
    r"^\s+([0-9a-f]+):"
    r"\s+([0-9a-f]{2}(?: [0-9a-f]{2})*)"
    r"(?:\s+([^\s]+)(?:\s+(.+?)\s*(?:# (0x[0-9a-f]+))?)?)?\s*$",
    re.MULTILINE,
)
RE_ASM_EXPRESSION = re.compile(
    r"([DQ]WORD) PTR \["
    r"([a-z0-9]{3})"
    r"(?:\+([a-z0-9]{3})\*([\d+]))?"
    r"(?:\+(0x[0-9a-f]+))?"
    r"\]"
)
PYMODULE_STRUCT = struct.Struct("x" * 40 + "LLlL")
PYMETHOD_STRUCT = struct.Struct("LLixxxxL")


handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s")
)
logger = logging.getLogger("pyso_extract")
handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


@dataclass
class AssemblyInstruction:
    loc_to_symbol: dict
    line: str
    data: str
    instruction: Optional[str]
    args: Optional[str]
    address: Optional[str]

    def __repr__(self):
        if self.symbol_name:
            symbols_identifier = f"# [{self.symbol_name}]"
        elif self.address:
            symbols_identifier = f"# [{self.address}]"
        else:
            symbols_identifier = ""

        return "".join(
            [
                self.line.rjust(8),
                ":       ",
                (self.data or "").ljust(24),
                (self.instruction or "").ljust(7),
                (self.args or "").ljust(30),
                symbols_identifier.ljust(20),
            ]
        )

    @property
    def size(self):
        length = len(self.data) + 1
        assert length % 3 == 0
        assert self.data.count(" ") == (length // 3 - 1)
        return length // 3

    @property
    def symbol_name(self):
        return self.loc_to_symbol.get(self.address)


class Tracers(Enum):
    MODULE = "MODULE"
    SUBMODULE = "SUBMODULE"
    MODULE_DICT = "MODULE_DICT"
    UNKNOWN = "UNKNOWN"


def initfunc_name(name):
    # See https://docs.python.org/3/extending/building.html#c.PyInit_modulename
    try:
        suffix = b"_" + name.encode("ascii")
    except UnicodeEncodeError:
        suffix = b"U_" + name.encode("punycode").replace(b"-", b"_")
    return "PyInit" + suffix.decode("ascii")
