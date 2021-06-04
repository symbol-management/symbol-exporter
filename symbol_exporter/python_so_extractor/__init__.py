__all__ = ("CompiledPythonLib",)

import pathlib

import os

os.environ["PWNLIB_NOTERM"] = "1"
os.environ["PWNLIB_SILENT"] = "1"

import pwn

from .utils import (
    ASM_PATTERN,
    RE_ASM_EXPRESSION,
    PYMODULE_STRUCT,
    PYMETHOD_STRUCT,
    logger,
    AssemblyInstruction,
    Tracers,
    initfunc_name,
)
from ..ast_symbol_extractor import SymbolType


class CompiledPythonLib:
    def __init__(self, filename):
        self.filename = pathlib.Path(filename)
        self.elf = pwn.ELF(filename)
        self._disassembled_cache = {}
        self._loc_to_symbol = {}

        # Find the locations of relaxant functions in the file
        for symbol_name, symbol_loc in self.elf.symbols.items():
            if symbol_name.startswith(("got.", "plt.")):
                continue
            symbol_loc = hex(symbol_loc)
            logger.debug("Found symbol for %s at %s", symbol_name, symbol_loc)
            self._loc_to_symbol[symbol_loc] = symbol_name

    @property
    def module_name(self):
        return self.filename.name.split(".")[0]

    def find_symbols(self):
        """Disassemble the PyInit function of the module and return symbols"""
        if not hasattr(self, "_results"):
            self._results = {
                "methods": [],
                "objects": [],
            }
            self._registers = {"stack": []}
            self._emulate(initfunc_name(self.module_name))
            del self._registers
        return self._results

    def _disassemble_symbol(self, function_name: str):
        if function_name not in self._disassembled_cache:
            init_asm = self.elf.functions[function_name].disasm()
            instructions = []
            logger.debug("Disassembled function (%s):", function_name)
            for line in init_asm.split("\n"):
                match = ASM_PATTERN.fullmatch(line)
                assert match, line
                instruction = AssemblyInstruction(self._loc_to_symbol, *match.groups())
                instructions.append(instruction)
                logger.debug(instruction)
            self._disassembled_cache[function_name] = instructions
        return self._disassembled_cache[function_name]

    def _emulate(self, function_name):
        registers = self._registers
        instructions = self._disassemble_symbol(function_name)

        # Parse the assembly calling the parser functions in self._known_symbols when needed
        for instruction in instructions:
            logger.debug("Executing: %r", instruction)
            registers["rip"] = hex(int(instruction.line, 16) + instruction.size)

            if instruction.instruction in ["lea"]:
                destination, source = map(str.strip, instruction.args.split(","))
                registers[destination] = instruction.address

            elif instruction.instruction in ["add"]:
                destination, source = map(str.strip, instruction.args.split(","))
                current_value = registers.get(destination, "0x0")
                # FIXME (current_value and)
                if current_value and current_value != Tracers.UNKNOWN:
                    registers[destination] = hex(int(current_value, 16) + int(source, 16))

            elif instruction.instruction in ["sub"]:
                destination, source = map(str.strip, instruction.args.split(","))
                current_value = registers.get(destination, "0x0")
                # FIXME (current_value and)
                if current_value and current_value != Tracers.UNKNOWN:
                    registers[destination] = hex(int(current_value, 16) - int(source, 16))

            elif instruction.instruction in ["xor"]:
                destination, source = map(str.strip, instruction.args.split(","))
                if destination == source:
                    # https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/x64-architecture
                    # FIXME
                    # if destination == "r15d":
                    #     destination = "r15"
                    registers[destination] = "0x0"

            elif instruction.instruction in ["mov"]:
                destination, source = map(str.strip, instruction.args.split(","))

                try:
                    if source in registers:
                        registers[destination] = registers[source]
                    elif source.startswith("0x"):
                        assert int(source, 16) >= 0, source
                        registers[destination] = source
                    elif match := RE_ASM_EXPRESSION.fullmatch(source):
                        size, src, offset_reg, multiplier, offset_idx = match.groups()
                        assert not src.startswith("0x"), src

                        if registers[src] == Tracers.UNKNOWN:
                            idx = Tracers.UNKNOWN
                        else:
                            idx = int(registers[src], 16)

                        if idx != Tracers.UNKNOWN and offset_idx:
                            idx += int(offset_idx, 16)

                        if idx != Tracers.UNKNOWN and offset_reg:
                            if registers[offset_reg] == Tracers.UNKNOWN:
                                idx = Tracers.UNKNOWN
                            elif int(registers[offset_reg], 16) > 0:
                                idx += self.elf.u64(int(registers[offset_reg], 16)) * int(multiplier)

                        if idx == Tracers.UNKNOWN:
                            registers[destination] = Tracers.UNKNOWN
                        elif idx > 0:
                            registers[destination] = hex(getattr(self.elf, {"DWORD": "u32", "QWORD": "u64"}[size])(idx))
                        else:
                            raise Exception()
                except Exception:
                    logger.warning("Failed to fill %r from %r", destination, instruction)
                    registers[destination] = Tracers.UNKNOWN

            elif instruction.instruction in ["push"]:
                (source,) = map(str.strip, instruction.args.split(","))
                registers["stack"] += [registers.get(source)]

            elif instruction.instruction in ["pop"]:
                (destination,) = map(str.strip, instruction.args.split(","))
                if registers["stack"]:
                    registers[destination] = registers["stack"].pop()
                else:
                    logger.warning("Tried to pop but the stack is empty!?")

            elif instruction.instruction in ["call", "jmp"]:
                if instruction.address:
                    address = instruction.address
                else:
                    address = instruction.args
                symbol_name = self._loc_to_symbol.get(address)
                logger.debug(
                    "Calling %s (%s) with register state:\n    %r",
                    address,
                    symbol_name,
                    registers,
                )
                if symbol_name in self._known_symbols:
                    self._known_symbols[symbol_name](instruction)
                elif symbol_name in self.elf.functions:
                    self._emulate(symbol_name)
                else:
                    logger.debug(
                        "Skipping call to %s (%s) as function definition is not available",
                        address,
                        symbol_name,
                    )
                    # TODO Maybe this should be a large negative value instead?
                    registers["rax"] = Tracers.UNKNOWN

    @property
    def _known_symbols(self):
        return {
            "PyModule_Create2": self._parse_create,
            "PyModuleDef_Init": self._parse_create,
            "PyModule_New": self._parse_new_submodule,
            "PyModule_NewObject": self._parse_new_submodule,
            "PyModule_AddObject": self._parse_add_object,
            "PyModule_AddIntConstant": self._parse_add_object,
            "PyModule_AddStringConstant": self._parse_add_object,
            "PyModule_GetDict": self._PyModule_GetDict,
            "PyDict_SetItemString": self._PyDict_SetItemString,
        }

    def _parse_create(self, call: AssemblyInstruction):
        module = self._registers["rdi"]
        if module == Tracers.UNKNOWN:
            logger.error("Failed to trace module struct")
            self._registers["rax"] = Tracers.UNKNOWN
            return

        module_struct_data = self.elf.read(int(module, base=16), PYMODULE_STRUCT.size)
        logger.debug("parse_module: module_struct_data is %s", list(map(hex, module_struct_data)))
        name, docs, size, methods_idx = PYMODULE_STRUCT.unpack(module_struct_data)
        assert name != 0, name
        name = self.elf.string(name).decode()
        if docs == 0:
            docs = None
        else:
            docs = self.elf.string(docs).decode()
        logger.debug("parse_module: Found module named %s", name)
        methods = []
        if methods_idx == 0:
            logger.debug("parse_module: No methods found, methods_idx is null")
        else:
            offset = 0
            while True:
                data = self.elf.read(methods_idx + offset, PYMETHOD_STRUCT.size)
                offset += PYMETHOD_STRUCT.size
                (
                    method_name,
                    method_func,
                    method_flags,
                    method_doc,
                ) = PYMETHOD_STRUCT.unpack(data)
                if method_name == 0:
                    break
                method_name = self.elf.string(method_name).decode()
                if method_doc == 0:
                    method_doc = None
                else:
                    method_doc = self.elf.string(method_doc).decode()
                methods.append({"name": method_name, "docstring": method_doc})
                logger.info(
                    "_parse_create: Found %s in %s at %s",
                    method_name,
                    name,
                    hex(method_func),
                )

        self._results["name"] = name
        self._results["docstring"] = docs
        self._results["methods"].extend(methods)
        self._registers["rax"] = Tracers.MODULE

    def _parse_new_submodule(self, call: AssemblyInstruction):
        if call.symbol_name == "PyModule_New":
            object_name = self.elf.string(int(self._registers["rdi"], 16)).decode()
        else:
            raise NotImplementedError(call.symbol_name)
        logger.info("_parse_new_submodule: Found submodule %s", object_name)
        self._registers["rax"] = Tracers.SUBMODULE

    def _parse_add_object(self, call: AssemblyInstruction):
        if self._registers["rdi"] == Tracers.MODULE:
            object_name = self.elf.string(int(self._registers["rsi"], 16)).decode()
            self._results["objects"].append({"name": object_name})
            logger.info("_parse_add_object: Found %s", object_name)
        else:
            logger.warning("Called _parse_add_object with rdi=%s", self._registers["rdi"])

    def _PyModule_GetDict(self, call: AssemblyInstruction):
        if self._registers["rdi"] == Tracers.MODULE:
            self._registers["rax"] = Tracers.MODULE_DICT
        else:
            self._registers["rax"] = None

    def _PyDict_SetItemString(self, call: AssemblyInstruction):
        if self._registers["rdi"] == Tracers.MODULE_DICT:
            object_name = self.elf.string(int(self._registers["rsi"], 16)).decode()
            logger.info(
                "Found call %s(module.__dict__, %s, %s)",
                call.symbol_name,
                object_name,
                self._registers["rdx"],
            )
            self._results["objects"] += [{"name": object_name}]


def c_symbols_to_datamodel(symbols):
    top_level_import = symbols["name"]
    output_data = {top_level_import: {"type": SymbolType.MODULE, "data": {}}}
    for method in symbols["methods"]:
        output_data[f"{top_level_import}.{method['name']}"] = dict(type=SymbolType.FUNCTION, data={})
    for object in symbols["objects"]:
        output_data[f"{top_level_import}.{object['name']}"] = dict(type=SymbolType.CONSTANT, data={})
    return output_data


def parse_so(filename, top_dir):
    module_path = (str(filename.parent).replace(f"{top_dir}/", "").replace('lib-dynload', '').replace("/", "."))
    s = c_symbols_to_datamodel(CompiledPythonLib(str(filename)).find_symbols())
    # cpython SOs don't have module_paths, they are all top level, but others do
    if module_path:
        s = {".".join([module_path, k]): v for k, v in s.items()}
    return s
