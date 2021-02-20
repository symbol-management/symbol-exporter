import argparse
from dataclasses import dataclass
import re
import struct
from typing import Optional
import logging
from pprint import pprint

import pwn

ASM_PATTERN = re.compile(r"^\s+([0-9a-f]+):\s+([0-9a-f]{2}(?: [0-9a-f]{2})*)(?:\s+([^\s]+)(?:\s+(.+?)\s*(?:# (0x[0-9a-f]+))?)?)?\s*$", re.MULTILINE)
PYMODULE_STRUCT = struct.Struct("x"*40 + "LLlL")
PYMETHOD_STRUCT = struct.Struct("LLixxxxL")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


@dataclass
class AssemblyInstruction:
    loc_to_symbol: dict
    line: str
    data: str
    instruction: Optional[str]
    args: Optional[str]
    address: Optional[str]

    def __repr__(self):
        return "".join([
            self.line.rjust(8),
            ":       ",
            (self.data or "").ljust(24),
            (self.instruction or "").ljust(7),
            (self.args or "").ljust(30),
            (f"# [{self.symbol_name}]" if self.symbol_name else "").ljust(20),
        ])

    @property
    def symbol_name(self):
        return self.loc_to_symbol.get(self.address)



def initfunc_name(name):
    # See https://docs.python.org/3/extending/building.html#c.PyInit_modulename
    try:
        suffix = b'_' + name.encode('ascii')
    except UnicodeEncodeError:
        suffix = b'U_' + name.encode('punycode').replace(b'-', b'_')
    return 'PyInit' + suffix.decode("ascii")


def parse_create(elf, call: AssemblyInstruction, most_recent: dict, results: dict):
    module = most_recent["lea"]

    module_struct_data = elf.read(int(module.address, base=16), PYMODULE_STRUCT.size)
    logger.debug("parse_module: module_struct_data is %s", list(map(hex, module_struct_data)))
    name, docs, size, methods_idx = PYMODULE_STRUCT.unpack(module_struct_data)
    assert name != 0, name
    name = elf.string(name).decode()
    if docs == 0:
        docs = None
    else:
        docs = elf.string(docs).decode()
    logger.debug("parse_module: Found module named %s", name)
    methods = []
    if methods_idx == 0:
        pass
        logger.debug("parse_module: No methods found, methods_idx is null")
    else:
        offset = 0
        while True:
            data = elf.read(methods_idx + offset, PYMETHOD_STRUCT.size)
            offset += PYMETHOD_STRUCT.size
            if all(d == 0 for d in data):
                break
            method_name, method_func, method_flags, method_doc = PYMETHOD_STRUCT.unpack(data)
            method_name = elf.string(method_name).decode()
            if method_doc == 0:
                method_doc = None
            else:
                method_doc = elf.string(method_doc).decode()
            methods.append({"name": method_name, "docstring": method_doc})
            logger.debug(
                "parse_create: Found %s in %s at %s",
                method_name, name, hex(method_func)
            )

    results["name"] = name
    results["docstring"] = docs
    results["methods"].extend(methods)


def parse_add_object(elf, call: AssemblyInstruction, most_recent: dict, results: dict):
    object_name = elf.string(int(most_recent["lea"].address, 16)).decode()
    results["objects"].append({"name": object_name})
    logger.debug("parse_add_object: Found %s", object_name)


KNOWN_SYMBOLS = {
    "PyModule_Create2": parse_create,
    "PyModuleDef_Init": parse_create,
    "PyModule_AddObject": parse_add_object,
    "PyModule_AddIntConstant": parse_add_object,
}


def parse_file(filename, module_name):
    elf = pwn.ELF(filename)

    # Find the locations of relaxant functions in the file
    loc_to_symbol = {}
    for symbol_name, symbol_loc in elf.symbols.items():
        symbol_loc = hex(symbol_loc)
        logger.debug("Found symbol for %s at %s", symbol_name, symbol_loc)
        loc_to_symbol[symbol_loc] = symbol_name

    # Disassemble the PyInit function of the module
    init_func = initfunc_name(module_name)
    init_asm = elf.functions[init_func].disasm()
    instructions = []
    logger.debug("Disassembled initialisation function (%s):", init_func)
    for line in init_asm.split("\n"):
        match = ASM_PATTERN.fullmatch(line)
        assert match, line
        instruction = AssemblyInstruction(loc_to_symbol, *match.groups())
        instructions.append(instruction)
        logger.debug(instruction)

    # Parse the assembly calling the parser functions KNOWN_SYMBOLS when needed
    most_recent = {}
    results = {
        "methods": [],
        "objects": [],
    }
    for instruction in instructions:
        most_recent[instruction.instruction] = instruction
        if instruction.instruction != "call":
            continue
        symbol_name = loc_to_symbol.get(instruction.address)
        if symbol_name in KNOWN_SYMBOLS:
            KNOWN_SYMBOLS[symbol_name](elf, instruction, most_recent, results)

    return results


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("module_name")
    parser.add_argument("--compare")
    args = parser.parse_args()
    results = parse_file(args.filename, args.module_name)

    if args.compare:
        import importlib
        module = importlib.import_module(args.compare)
        expected = {s for s in dir(module) if not re.fullmatch(r"__.+__", s)}
        actual = {x["name"] for x in results["methods"]}
        actual |= {x["name"] for x in results["objects"]}
        if actual - expected:
            raise NotImplementedError("Found unexpected keys", actual - expected)
        if expected - actual:
            logger.warning("Failed to find some keys: %s", expected - actual)


if __name__ == "__main__":
    parse_args()
