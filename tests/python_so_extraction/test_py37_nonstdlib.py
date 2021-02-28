import pytest

from . import compare


def test_regex__regex():
    expected = {
        "fold_case",
        "copyright",
        "has_property_value",
        "get_expand_on_folding",
        "compile",
        "MAGIC",
        "CODE_SIZE",
        "get_properties",
        "get_all_cases",
        "get_code_size",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/regex-2020.5.14-py37h8f50634_0.tar.bz2",
        "f1ed5af8034e3e9f9593c8bfe5e4fd53",
        "lib/python3.7/site-packages/regex/_regex.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_rapidfuzz_levenshtein():
    expected = {
        "weighted_distance",
        "normalized_distance",
        "normalized_weighted_distance",
        "distance",
    }
    compare(
        "https://anaconda.org/conda-forge/rapidfuzz/0.11.0/download/linux-64/rapidfuzz-0.11.0-py37h3340039_0.tar.bz2",
        "2fdbb5185f34665a3cbf93f543cc6846",
        "lib/python3.7/site-packages/rapidfuzz/levenshtein.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_rapidfuzz_fuzz():
    expected = {
        "token_set_ratio",
        "quick_lev_ratio",
        "token_sort_ratio",
        "partial_token_ratio",
        "partial_token_sort_ratio",
        "token_ratio",
        "partial_token_set_ratio",
        "ratio",
        "QRatio",
        "WRatio",
        "partial_ratio",
    }
    compare(
        "https://anaconda.org/conda-forge/rapidfuzz/0.11.0/download/linux-64/rapidfuzz-0.11.0-py37h3340039_0.tar.bz2",
        "2fdbb5185f34665a3cbf93f543cc6846",
        "lib/python3.7/site-packages/rapidfuzz/fuzz.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_rapidfuzz_utils():
    expected = {"default_process"}
    compare(
        "https://anaconda.org/conda-forge/rapidfuzz/0.11.0/download/linux-64/rapidfuzz-0.11.0-py37h3340039_0.tar.bz2",
        "2fdbb5185f34665a3cbf93f543cc6846",
        "lib/python3.7/site-packages/rapidfuzz/utils.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_markupsafe__speedups():
    expected = {"escape", "soft_unicode", "escape_silent"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/markupsafe-1.1.1-py37h8f50634_1.tar.bz2",
        "3a1f9e93d5bed65a9875eb2e5805cf0d",
        "lib/python3.7/site-packages/markupsafe/_speedups.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test__yaml():
    expected = {
        "ScannerError",
        "SequenceStartEvent",
        "RepresenterError",
        "ScalarEvent",
        "ValueToken",
        "ConstructorError",
        "StreamEndEvent",
        "TagToken",
        "BlockEndToken",
        "FlowEntryToken",
        "ParserError",
        "CParser",
        "AliasEvent",
        "EmitterError",
        "DirectiveToken",
        "BlockEntryToken",
        "get_version",
        "yaml",
        "get_version_string",
        "SequenceEndEvent",
        "ScalarToken",
        "StreamEndToken",
        "YAMLError",
        "StreamStartToken",
        "DocumentStartEvent",
        "DocumentStartToken",
        "ScalarNode",
        "DocumentEndEvent",
        "SerializerError",
        "FlowMappingStartToken",
        "FlowSequenceEndToken",
        "StreamStartEvent",
        "Mark",
        "KeyToken",
        "AliasToken",
        "ReaderError",
        "__pyx_unpickle_Mark",
        "MappingNode",
        "BlockSequenceStartToken",
        "MappingEndEvent",
        "BlockMappingStartToken",
        "FlowSequenceStartToken",
        "SequenceNode",
        "FlowMappingEndToken",
        "DocumentEndToken",
        "ComposerError",
        "CEmitter",
        "MappingStartEvent",
        "AnchorToken",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pyyaml-5.3.1-py37h8f50634_0.tar.bz2",
        "13495f8abe3fa4e8905439257d1132d4",
        "lib/python3.7/site-packages/_yaml.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test__pylief():
    pytest.skip("Something is very wrong with this test")
    expected = {
        "N4LIEF12ref_iteratorIRSt6vectorINS_2PE9RichEntryESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "INFO",
        "LOGGING_LEVEL",
        "MachO",
        "MODES",
        "XCODE",
        "integrity_error",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF4NoteESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "SPARC",
        "GLOBAL",
        "OBJECT_TYPES",
        "to_json_from_abstract",
        "DictStringVersion",
        "OAT",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF13SymbolVersionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "MIPS32",
        "PPC",
        "MCLASS",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_2PE15RelocationEntryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF12ref_iteratorIRSt6vectorINS_2PE6ImportESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "ART",
        "Relocation",
        "N4LIEF12ref_iteratorISt6vectorIPNS_5MachO10ExportInfoESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF15filter_iteratorISt6vectorIPNS_5MachO6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "to_json",
        "V8",
        "N4LIEF15filter_iteratorISt6vectorIPNS_3ELF10RelocationESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF12ref_iteratorISt6vectorIPNS_6SymbolESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "ARM64",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF23SymbolVersionDefinitionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_2PE12ResourceNodeESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF12ref_iteratorISt6vectorIPNS_3ELF6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "VERBOSE",
        "N4LIEF12ref_iteratorIRKSt6vectorINS_2PE18ResourceDialogItemESaIS3_EEN9__gnu_cxx17__normal_iteratorIPKS3_S5_EEEE",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_5MachO6BinaryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF12DynamicEntryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "is_oat",
        "Symbol",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_5MachO6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "is_macho",
        "Header",
        "parser_error",
        "N4LIEF12ref_iteratorIRSt6vectorINS_2PE11ExportEntryESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "N4LIEF12ref_iteratorISt6vectorIPNS_2PE7SectionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "MIPS",
        "N4LIEF12ref_iteratorISt6vectorIPNS_5MachO14SegmentCommandESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "not_found",
        "MIPS32R6",
        "N4LIEF12ref_iteratorISt6vectorIPNS_2PE13DataDirectoryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "Binary",
        "ARM",
        "bad_file",
        "breakp",
        "N4LIEF15filter_iteratorISt6vectorIPNS_3ELF6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "exception",
        "N4LIEF12ref_iteratorISt6vectorIPNS_7SectionESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "DEBUG",
        "MIPS3",
        "is_dex",
        "ListLangCodeItem",
        "UNDEFINED",
        "N4LIEF12ref_iteratorISt6vectorIPNS_10RelocationESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "VDEX",
        "hash",
        "is_pe",
        "dex_version",
        "oat_version",
        "MACHO",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF24SymbolVersionRequirementESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "shell",
        "DEX",
        "LITTLE",
        "Android",
        "M32",
        "is_art",
        "not_supported",
        "N4LIEF12ref_iteratorISt6vectorIPNS_5MachO11LoadCommandESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF12ref_iteratorIRSt6vectorINS_2PE6SymbolESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "bad_format",
        "N4LIEF12ref_iteratorISt6vectorIPNS_5MachO7SectionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "M64",
        "N4LIEF12ref_iteratorIRSt3setIPNS_5MachO10RelocationENS2_6KeyCmpIS3_EESaIS4_EESt23_Rb_tree_const_iteratorIS4_EEE",
        "parse",
        "MIPSGP64",
        "ERROR",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF27SymbolVersionAuxRequirementESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "LIBRARY",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF10RelocationESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "V7",
        "is_elf",
        "N4LIEF12ref_iteratorIRSt6vectorINS_2PE11ImportEntryESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE",
        "OBJECT",
        "ARCHITECTURES",
        "Logger",
        "pe_bad_section_name",
        "M16",
        "N4LIEF12ref_iteratorISt6vectorIPNS_5MachO12DylibCommandESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "NONE",
        "Section",
        "FATAL",
        "vdex_version",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF16SymbolVersionAuxESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "MIPS64",
        "type_error",
        "art_version",
        "ENDIANNESS",
        "N4LIEF12ref_iteratorIRKSt6vectorINS_2PE4x509ESaIS3_EEN9__gnu_cxx17__normal_iteratorIPKS3_S5_EEEE",
        "TRACE",
        "BIG",
        "is_vdex",
        "THUMB",
        "builder_error",
        "SYSZ",
        "Object",
        "V9",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_2PE10RelocationESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "conversion_error",
        "ELF",
        "read_out_of_bound",
        "pe_error",
        "PE",
        "WARNING",
        "EXE_FORMATS",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF7SectionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "N4LIEF12ref_iteratorISt6vectorIPNS_5MachO11BindingInfoESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "X86",
        "N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF7SegmentESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE",
        "EXECUTABLE",
        "UNKNOWN",
        "INTEL",
        "corrupted",
        "not_implemented",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/py-lief-0.9.0-py37he1b5a44_1.tar.bz2",
        "6a37ab0dd211238a4d13d8ea1269620f",
        "lib/python3.7/site-packages/_pylief.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__XOR():
    expected = {"key_size", "error", "new", "block_size"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_XOR.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__AES():
    expected = {
        "key_size",
        "MODE_OFB",
        "MODE_CTR",
        "MODE_ECB",
        "MODE_CBC",
        "new",
        "MODE_PGP",
        "MODE_CFB",
        "block_size",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_AES.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__Blowfish():
    expected = {
        "key_size",
        "MODE_CFB",
        "MODE_PGP",
        "MODE_CBC",
        "MODE_OFB",
        "MODE_CTR",
        "MODE_ECB",
        "block_size",
        "new",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_Blowfish.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__ARC4():
    expected = {"key_size", "block_size", "error", "new"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_ARC4.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__DES():
    expected = {
        "MODE_CBC",
        "MODE_ECB",
        "MODE_CTR",
        "MODE_CFB",
        "MODE_PGP",
        "MODE_OFB",
        "key_size",
        "new",
        "block_size",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_DES.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__CAST():
    expected = {
        "key_size",
        "MODE_CTR",
        "MODE_CFB",
        "block_size",
        "MODE_OFB",
        "MODE_CBC",
        "MODE_PGP",
        "MODE_ECB",
        "new",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_CAST.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__DES3():
    expected = {
        "MODE_CBC",
        "MODE_CTR",
        "MODE_ECB",
        "MODE_CFB",
        "MODE_OFB",
        "key_size",
        "block_size",
        "new",
        "MODE_PGP",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_DES3.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Cipher__ARC2():
    expected = {
        "MODE_CTR",
        "MODE_CFB",
        "MODE_PGP",
        "MODE_OFB",
        "block_size",
        "key_size",
        "new",
        "MODE_ECB",
        "MODE_CBC",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Cipher/_ARC2.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Util__counter():
    expected = {"_newLE", "_newBE"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Util/_counter.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


@pytest.mark.xfail(reason="TODO")
def test_Crypto_Util_strxor():
    expected = {"strxor_c", "strxor"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Util/strxor.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Hash__MD4():
    expected = {"digest_size", "block_size", "new"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Hash/_MD4.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Hash__SHA224():
    expected = {"digest_size", "new", "block_size"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Hash/_SHA224.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Hash__SHA384():
    expected = {"new", "digest_size", "block_size"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Hash/_SHA384.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Hash__RIPEMD160():
    expected = {"new", "block_size", "digest_size"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Hash/_RIPEMD160.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Hash__MD2():
    expected = {"new", "digest_size", "block_size"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Hash/_MD2.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Hash__SHA512():
    expected = {"block_size", "digest_size", "new"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Hash/_SHA512.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_Crypto_Hash__SHA256():
    expected = {"new", "block_size", "digest_size"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycrypto-2.6.1-py37h8f50634_1004.tar.bz2",
        "972c15bab1559d0dec151d1486d80f0d",
        "lib/python3.7/site-packages/Crypto/Hash/_SHA256.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_typed_ast__ast27():
    expected = {
        "List",
        "Index",
        "Pass",
        "ListComp",
        "Str",
        "arguments",
        "Del",
        "For",
        "LShift",
        "In",
        "BitOr",
        "parse",
        "NotEq",
        "cmpop",
        "Or",
        "Param",
        "SetComp",
        "With",
        "comprehension",
        "Repr",
        "Assert",
        "Tuple",
        "Interactive",
        "Ellipsis",
        "BinOp",
        "Lambda",
        "And",
        "Num",
        "boolop",
        "stmt",
        "Eq",
        "unaryop",
        "Assign",
        "TryExcept",
        "BitAnd",
        "BitXor",
        "operator",
        "ExceptHandler",
        "AugLoad",
        "Expression",
        "Div",
        "Name",
        "Attribute",
        "Break",
        "AST",
        "Slice",
        "Suite",
        "mod",
        "Call",
        "LtE",
        "Invert",
        "USub",
        "keyword",
        "slice",
        "PyCF_ONLY_AST",
        "FunctionDef",
        "Load",
        "TryFinally",
        "AugStore",
        "Return",
        "Raise",
        "ExtSlice",
        "Set",
        "Sub",
        "Expr",
        "Import",
        "Not",
        "UAdd",
        "GeneratorExp",
        "Yield",
        "Dict",
        "FunctionType",
        "excepthandler",
        "Continue",
        "IfExp",
        "FloorDiv",
        "NotIn",
        "Pow",
        "UnaryOp",
        "RShift",
        "Module",
        "DictComp",
        "IsNot",
        "Print",
        "ClassDef",
        "Compare",
        "expr",
        "Subscript",
        "Add",
        "Global",
        "GtE",
        "type_ignore",
        "Mod",
        "TypeIgnore",
        "While",
        "expr_context",
        "Store",
        "BoolOp",
        "Is",
        "ImportFrom",
        "Gt",
        "alias",
        "Exec",
        "If",
        "Lt",
        "Mult",
        "Delete",
        "AugAssign",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/typed-ast-1.4.1-py37h516909a_0.tar.bz2",
        "8ce1dc4eaf70204b3a3544f52a5939f8",
        "lib/python3.7/site-packages/typed_ast/_ast27.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_typed_ast__ast3():
    expected = {
        "Suite",
        "Assign",
        "PyCF_ONLY_AST",
        "YieldFrom",
        "Module",
        "For",
        "type_ignore",
        "Assert",
        "keyword",
        "Raise",
        "In",
        "Lt",
        "alias",
        "LShift",
        "Ellipsis",
        "slice",
        "And",
        "Continue",
        "arg",
        "Mult",
        "Tuple",
        "Name",
        "FloorDiv",
        "DictComp",
        "AugAssign",
        "Add",
        "ExtSlice",
        "NotIn",
        "mod",
        "Await",
        "RShift",
        "Del",
        "Interactive",
        "withitem",
        "Nonlocal",
        "GtE",
        "Lambda",
        "While",
        "Attribute",
        "unaryop",
        "Not",
        "ListComp",
        "FormattedValue",
        "Yield",
        "Gt",
        "Mod",
        "Call",
        "Sub",
        "Pow",
        "Global",
        "Store",
        "boolop",
        "ExceptHandler",
        "AsyncFunctionDef",
        "Try",
        "ImportFrom",
        "MatMult",
        "Param",
        "excepthandler",
        "BitAnd",
        "BitXor",
        "operator",
        "comprehension",
        "ClassDef",
        "arguments",
        "expr_context",
        "Set",
        "AugStore",
        "LtE",
        "IsNot",
        "Dict",
        "BoolOp",
        "_parse",
        "JoinedStr",
        "Expr",
        "List",
        "Slice",
        "USub",
        "Constant",
        "SetComp",
        "FunctionDef",
        "BitOr",
        "AnnAssign",
        "Index",
        "TypeIgnore",
        "Bytes",
        "AugLoad",
        "UAdd",
        "Is",
        "expr",
        "With",
        "Or",
        "Pass",
        "Div",
        "UnaryOp",
        "Compare",
        "FunctionType",
        "NotEq",
        "Num",
        "If",
        "IfExp",
        "Break",
        "NameConstant",
        "Starred",
        "Delete",
        "AsyncFor",
        "AsyncWith",
        "stmt",
        "AST",
        "Invert",
        "Eq",
        "Subscript",
        "GeneratorExp",
        "Str",
        "BinOp",
        "Load",
        "Return",
        "Import",
        "Expression",
        "cmpop",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/typed-ast-1.4.1-py37h516909a_0.tar.bz2",
        "8ce1dc4eaf70204b3a3544f52a5939f8",
        "lib/python3.7/site-packages/typed_ast/_ast3.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test__scrypt():
    expected = set()
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/scrypt-0.8.15-py37hb09aad4_0.tar.bz2",
        "7afa5bf698f27a721f08fb42accce2fc",
        "lib/python3.7/site-packages/_scrypt.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


@pytest.mark.xfail(reason="TODO")
def test__cffi_backend():
    expected = {
        "set_errno",
        "RTLD_DEEPBIND",
        "from_buffer",
        "gcp",
        "_init_cffi_1_0_external_module",
        "get_errno",
        "typeoffsetof",
        "unpack",
        "RTLD_LAZY",
        "_C_API",
        "cast",
        "sizeof",
        "new_struct_type",
        "new_primitive_type",
        "new_function_type",
        "release",
        "RTLD_GLOBAL",
        "new_pointer_type",
        "newp",
        "typeof",
        "FFI_CDECL",
        "string",
        "callback",
        "Lib",
        "new_union_type",
        "buffer",
        "new_enum_type",
        "memmove",
        "_testfunc",
        "load_library",
        "getcname",
        "_get_types",
        "newp_handle",
        "RTLD_LOCAL",
        "new_array_type",
        "RTLD_NODELETE",
        "_testbuff",
        "from_handle",
        "alignof",
        "complete_struct_or_union",
        "FFI_DEFAULT_ABI",
        "FFI",
        "rawaddressof",
        "RTLD_NOLOAD",
        "new_void_type",
        "_get_common_types",
        "RTLD_NOW",
    }
    compare(
        "https://anaconda.org/conda-forge/cffi/1.14.0/download/linux-64/cffi-1.14.0-py37hd463f26_0.tar.bz2",
        "e8f964de28087a1a68f5be2c4449f3b0",
        "lib/python3.7/site-packages/_cffi_backend.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_wrapt__wrappers():
    expected = {
        "BoundFunctionWrapper",
        "CallableObjectProxy",
        "ObjectProxy",
        "_FunctionWrapperBase",
        "PartialCallableObjectProxy",
        "FunctionWrapper",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/wrapt-1.12.1-py37h8f50634_1.tar.bz2",
        "d6f832e746eb1ebd18188296f0e3bb6f",
        "lib/python3.7/site-packages/wrapt/_wrappers.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_psutil__psutil_linux():
    expected = {
        "set_testing",
        "proc_cpu_affinity_set",
        "proc_ioprio_set",
        "version",
        "users",
        "DUPLEX_FULL",
        "DUPLEX_HALF",
        "net_if_duplex_speed",
        "linux_sysinfo",
        "DUPLEX_UNKNOWN",
        "proc_ioprio_get",
        "disk_partitions",
        "proc_cpu_affinity_get",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/psutil-5.7.0-py37h8f50634_1.tar.bz2",
        "9c5b3e84c0952a7cacb069c18ae1932a",
        "lib/python3.7/site-packages/psutil/_psutil_linux.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_psutil__psutil_posix():
    expected = {
        "setpriority",
        "net_if_flags",
        "net_if_addrs",
        "net_if_mtu",
        "getpriority",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/psutil-5.7.0-py37h8f50634_1.tar.bz2",
        "9c5b3e84c0952a7cacb069c18ae1932a",
        "lib/python3.7/site-packages/psutil/_psutil_posix.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_mamba_mamba_api():
    pytest.skip("Something is very wrong with this test")
    expected = {
        "SOLVER_SOLVABLE",
        "Transaction",
        "SOLVER_FLAG_SPLITPROVIDES",
        "SOLVER_FLAG_NEED_UPDATEPROVIDE",
        "SOLVER_FLAG_BEST_OBEY_POLICY",
        "SOLVER_NOAUTOSET",
        "SOLVER_NOTBYUSER",
        "calculate_channel_urls",
        "SOLVER_DISFAVOR",
        "SOLVER_ORUPDATE",
        "SOLVER_FLAG_IGNORE_RECOMMENDED",
        "SOLVER_FLAG_FOCUS_BEST",
        "Repo",
        "SOLVER_JOBMASK",
        "SOLVER_TARGETED",
        "SOLVER_WEAKENDEPS",
        "SOLVER_NOOP",
        "SOLVER_SOLVABLE_ONE_OF",
        "SOLVER_FLAG_KEEP_ORPHANS",
        "SOLVER_ERASE",
        "SOLVER_SOLVABLE_PROVIDES",
        "SOLVER_CLEANDEPS",
        "SOLVER_FLAG_ALLOW_UNINSTALL",
        "SOLVER_SELECTMASK",
        "SOLVER_FLAG_DUP_ALLOW_ARCHCHANGE",
        "PrefixData",
        "Context",
        "SOLVER_FLAG_ALLOW_ARCHCHANGE",
        "SOLVER_LOCK",
        "SubdirData",
        "Channel",
        "MAMBA_FORCE_REINSTALL",
        "QueryFormat",
        "SOLVER_FLAG_BREAK_ORPHANS",
        "SOLVER_FLAG_KEEP_EXPLICIT_OBSOLETES",
        "SOLVER_FLAG_ALLOW_DOWNGRADE",
        "SOLVER_FLAG_NO_INFARCHCHECK",
        "Path",
        "DownloadTargetList",
        "SOLVER_FLAG_DUP_ALLOW_VENDORCHANGE",
        "SOLVER_SETEV",
        "SOLVER_SETREPO",
        "SOLVER_SETEVR",
        "SOLVER_FLAG_FOCUS_INSTALLED",
        "SOLVER_FLAG_DUP_ALLOW_DOWNGRADE",
        "SOLVER_FLAG_NO_AUTOTARGET",
        "SOLVER_WEAK",
        "SOLVER_USERINSTALLED",
        "SOLVER_FLAG_YUM_OBSOLETES",
        "SOLVER_SETNAME",
        "SOLVER_FLAG_STRONG_RECOMMENDS",
        "Solver",
        "Query",
        "SOLVER_ALLOWUNINSTALL",
        "get_channel_urls",
        "SOLVER_FLAG_ALLOW_NAMECHANGE",
        "SOLVER_SOLVABLE_REPO",
        "SOLVER_SOLVABLE_NAME",
        "cache_fn_url",
        "create_cache_dir",
        "SOLVER_ESSENTIAL",
        "SOLVER_FLAG_URPM_REORDER",
        "SOLVER_SETMASK",
        "SOLVER_SETARCH",
        "SOLVER_FLAG_NO_UPDATEPROVIDE",
        "SOLVER_FLAG_ADD_ALREADY_RECOMMENDED",
        "SOLVER_DROP_ORPHANED",
        "Pool",
        "SOLVER_FORCEBEST",
        "MultiPackageCache",
        "SOLVER_FLAG_DUP_ALLOW_NAMECHANGE",
        "SOLVER_FLAG_ALLOW_VENDORCHANGE",
        "SOLVER_DISTUPGRADE",
        "SOLVER_SOLVABLE_ALL",
        "transmute",
        "SOLVER_MULTIVERSION",
        "SOLVER_UPDATE",
        "SOLVER_FLAG_INSTALL_ALSO_UPDATES",
        "MambaNativeException",
        "SOLVER_SETVENDOR",
        "SOLVER_FLAG_ONLY_NAMESPACE_RECOMMENDED",
        "SOLVER_VERIFY",
        "MAMBA_NO_DEPS",
        "SOLVER_INSTALL",
        "SOLVER_FAVOR",
        "MAMBA_ONLY_DEPS",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/mamba-0.7.14-py37h7f483ca_0.tar.bz2",
        "489d89d4fd43dca9cc491963e4586478",
        "lib/python3.7/site-packages/mamba/mamba_api.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_editdistance_bycython():
    expected = {"eval"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/editdistance-0.5.3-py37hcd2ae1e_3.tar.bz2",
        "e9c9fe028748305864f776ebdf7a823b",
        "lib/python3.7/site-packages/editdistance/bycython.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_aiohttp__http_writer():
    expected = {"istr", "_serialize_headers"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/aiohttp-3.7.3-py37h5e8e339_2.tar.bz2",
        "6002976673fcb4cc3d07f5c2c35e86de",
        "lib/python3.7/site-packages/aiohttp/_http_writer.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_aiohttp__frozenlist():
    expected = {"MutableSequence", "FrozenList", "__pyx_unpickle_FrozenList"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/aiohttp-3.7.3-py37h5e8e339_2.tar.bz2",
        "6002976673fcb4cc3d07f5c2c35e86de",
        "lib/python3.7/site-packages/aiohttp/_frozenlist.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_aiohttp__helpers():
    expected = {"__pyx_unpickle_reify", "reify"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/aiohttp-3.7.3-py37h5e8e339_2.tar.bz2",
        "6002976673fcb4cc3d07f5c2c35e86de",
        "lib/python3.7/site-packages/aiohttp/_helpers.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_aiohttp__http_parser():
    expected = {
        "_DeflateBuffer",
        "BadHttpMessage",
        "__pyx_unpickle_RawResponseMessage",
        "BadStatusLine",
        "hdrs",
        "HttpResponseParser",
        "LineTooLong",
        "PayloadEncodingError",
        "parse_url",
        "TransferEncodingError",
        "ContentLengthError",
        "_URL",
        "__pyx_unpickle_RawRequestMessage",
        "HttpRequestParser",
        "_CIMultiDictProxy",
        "_HttpVersion",
        "_HttpVersion11",
        "_StreamReader",
        "_HttpVersion10",
        "InvalidHeader",
        "InvalidURLError",
        "_EMPTY_PAYLOAD",
        "RawResponseMessage",
        "i",
        "RawRequestMessage",
        "_CIMultiDict",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/aiohttp-3.7.3-py37h5e8e339_2.tar.bz2",
        "6002976673fcb4cc3d07f5c2c35e86de",
        "lib/python3.7/site-packages/aiohttp/_http_parser.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_aiohttp__websocket():
    expected = {"_websocket_mask_cython"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/aiohttp-3.7.3-py37h5e8e339_2.tar.bz2",
        "6002976673fcb4cc3d07f5c2c35e86de",
        "lib/python3.7/site-packages/aiohttp/_websocket.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_multidict__multidict():
    expected = {
        "CIMultiDict",
        "MultiDict",
        "MultiDictProxy",
        "getversion",
        "istr",
        "CIMultiDictProxy",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/multidict-5.1.0-py37h5e8e339_1.tar.bz2",
        "39af34b76f594728f06fc6ed14b9db54",
        "lib/python3.7/site-packages/multidict/_multidict.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_ruamel_yaml_ext__ruamel_yaml():
    expected = {
        "ScalarToken",
        "MappingNode",
        "SequenceEndEvent",
        "ScannerError",
        "BlockEntryToken",
        "ConstructorError",
        "YAMLError",
        "ComposerError",
        "FlowSequenceEndToken",
        "DocumentStartEvent",
        "StreamEndToken",
        "TagToken",
        "ScalarNode",
        "SequenceStartEvent",
        "MappingEndEvent",
        "FlowMappingStartToken",
        "MappingStartEvent",
        "CEmitter",
        "get_version_string",
        "BlockEndToken",
        "StreamStartEvent",
        "EmitterError",
        "get_version",
        "__pyx_unpickle_Mark",
        "ReaderError",
        "Mark",
        "DocumentStartToken",
        "DocumentEndToken",
        "StreamEndEvent",
        "AliasToken",
        "DirectiveToken",
        "FlowEntryToken",
        "BlockMappingStartToken",
        "FlowSequenceStartToken",
        "ValueToken",
        "AliasEvent",
        "KeyToken",
        "BlockSequenceStartToken",
        "CParser",
        "FlowMappingEndToken",
        "AnchorToken",
        "DocumentEndEvent",
        "ParserError",
        "SerializerError",
        "StreamStartToken",
        "SequenceNode",
        "RepresenterError",
        "ScalarEvent",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/ruamel_yaml-0.15.80-py37h8f50634_1001.tar.bz2",
        "a7314a2fe6a28b4d6c8029c1e563f653",
        "lib/python3.7/site-packages/ruamel_yaml/ext/_ruamel_yaml.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_conda_package_handling_archive_utils_cy():
    expected = {"extract_file", "create_archive"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/conda-package-handling-1.6.0-py37h8f50634_2.tar.bz2",
        "c9e8d8dffd135b913beb4d333d603ae4",
        "lib/python3.7/site-packages/conda_package_handling/archive_utils_cy.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_yarl__quoting_c():
    expected = {
        "_Quoter",
        "_Unquoter",
        "i",
        "digits",
        "ascii_letters",
        "__pyx_unpickle__Quoter",
        "__pyx_unpickle__Unquoter",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/yarl-1.6.3-py37h5e8e339_1.tar.bz2",
        "11ee71d9c49f5d467c229917feaa0be0",
        "lib/python3.7/site-packages/yarl/_quoting_c.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test__ruamel_yaml():
    expected = {
        "FlowMappingEndToken",
        "YAMLError",
        "ScalarNode",
        "CEmitter",
        "MappingStartEvent",
        "DocumentEndToken",
        "StreamStartEvent",
        "SerializerError",
        "ValueToken",
        "StreamStartToken",
        "EmitterError",
        "RepresenterError",
        "Mark",
        "AliasToken",
        "MappingEndEvent",
        "SequenceEndEvent",
        "FlowEntryToken",
        "ParserError",
        "BlockEntryToken",
        "AnchorToken",
        "BlockSequenceStartToken",
        "SequenceStartEvent",
        "DocumentEndEvent",
        "FlowSequenceEndToken",
        "FlowMappingStartToken",
        "get_version_string",
        "ScannerError",
        "__pyx_unpickle_Mark",
        "KeyToken",
        "TagToken",
        "CParser",
        "ConstructorError",
        "ScalarEvent",
        "AliasEvent",
        "ComposerError",
        "BlockEndToken",
        "DocumentStartToken",
        "BlockMappingStartToken",
        "FlowSequenceStartToken",
        "get_version",
        "StreamEndEvent",
        "StreamEndToken",
        "ReaderError",
        "SequenceNode",
        "MappingNode",
        "ScalarToken",
        "DocumentStartEvent",
        "DirectiveToken",
    }
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/ruamel.yaml.clib-0.2.0-py37h8f50634_1.tar.bz2",
        "71717a66629f873f5283b5cdb0f995dc",
        "lib/python3.7/site-packages/_ruamel_yaml.cpython-37m-x86_64-linux-gnu.so",
        expected,
        xmissing=True,
    )


def test_coverage_tracer():
    expected = {"CFileDisposition", "CTracer"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/coverage-5.4-py37h5e8e339_0.tar.bz2",
        "e6ae2d570a84e7991e7d4be9ede77583",
        "lib/python3.7/site-packages/coverage/tracer.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_lazy_object_proxy_cext():
    expected = {"identity", "Proxy"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/lazy-object-proxy-1.4.3-py37h8f50634_2.tar.bz2",
        "ca5a654950e8cd78e7e749d0eeae56f1",
        "lib/python3.7/site-packages/lazy_object_proxy/cext.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )


def test_pycosat():
    expected = {"__version__", "itersolve", "solve"}
    compare(
        "https://conda.anaconda.org/conda-forge/linux-64/pycosat-0.6.3-py37h8f50634_1004.tar.bz2",
        "64e05681e3e672b8190688f7fe56ef46",
        "lib/python3.7/site-packages/pycosat.cpython-37m-x86_64-linux-gnu.so",
        expected,
    )
