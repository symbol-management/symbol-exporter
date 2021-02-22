import pytest

from symbol_exporter import python_so_extractor


def compare(filename, module_name, expected, *, xmissing=False):
    python_so_extractor.disassembled_cache = {}
    results = python_so_extractor.parse_file(filename, module_name)
    actual = {x["name"] for x in results["methods"]}
    actual |= {x["name"] for x in results["objects"]}
    diff = (actual - expected)
    assert not diff, (f"Found {len(diff)} extra keys", diff)
    diff = (expected - actual)
    if xmissing:
        assert diff, "Unexpectedly passed!"
        pytest.xfail(f"{len(diff)} out of {len(expected)} were not found (known issue)")
    else:
        assert not diff, (f"Failed to find {len(diff)} out of {len(expected)} keys", diff)


def test_regex__regex():
    expected = {'fold_case', 'copyright', 'has_property_value', 'get_expand_on_folding', 'compile', 'MAGIC', 'CODE_SIZE', 'get_properties', 'get_all_cases', 'get_code_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/regex/_regex.cpython-37m-x86_64-linux-gnu.so', '_regex', expected)


def test_rapidfuzz_levenshtein():
    expected = {'weighted_distance', 'normalized_distance', 'normalized_weighted_distance', 'distance'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/rapidfuzz/levenshtein.cpython-37m-x86_64-linux-gnu.so', 'levenshtein', expected)
  

def test_rapidfuzz_fuzz():
    expected = {'token_set_ratio', 'quick_lev_ratio', 'token_sort_ratio', 'partial_token_ratio', 'partial_token_sort_ratio', 'token_ratio', 'partial_token_set_ratio', 'ratio', 'QRatio', 'WRatio', 'partial_ratio'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/rapidfuzz/fuzz.cpython-37m-x86_64-linux-gnu.so', 'fuzz', expected)


def test_rapidfuzz_utils():
    expected = {'default_process'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/rapidfuzz/utils.cpython-37m-x86_64-linux-gnu.so', 'utils', expected)


def test_markupsafe__speedups():
    expected = {'escape', 'soft_unicode', 'escape_silent'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/markupsafe/_speedups.cpython-37m-x86_64-linux-gnu.so', '_speedups', expected)


def test__yaml():
    expected = {'ScannerError', 'SequenceStartEvent', 'RepresenterError', 'ScalarEvent', 'ValueToken', 'ConstructorError', 'StreamEndEvent', 'TagToken', 'BlockEndToken', 'FlowEntryToken', 'ParserError', 'CParser', 'AliasEvent', 'EmitterError', 'DirectiveToken', 'BlockEntryToken', 'get_version', 'yaml', 'get_version_string', 'SequenceEndEvent', 'ScalarToken', 'StreamEndToken', 'YAMLError', 'StreamStartToken', 'DocumentStartEvent', 'DocumentStartToken', 'ScalarNode', 'DocumentEndEvent', 'SerializerError', 'FlowMappingStartToken', 'FlowSequenceEndToken', 'StreamStartEvent', 'Mark', 'KeyToken', 'AliasToken', 'ReaderError', '__pyx_unpickle_Mark', 'MappingNode', 'BlockSequenceStartToken', 'MappingEndEvent', 'BlockMappingStartToken', 'FlowSequenceStartToken', 'SequenceNode', 'FlowMappingEndToken', 'DocumentEndToken', 'ComposerError', 'CEmitter', 'MappingStartEvent', 'AnchorToken'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/_yaml.cpython-37m-x86_64-linux-gnu.so', '_yaml', expected, xmissing=True)


def test__pylief():
    pytest.skip("Something is very wrong with this test")
    expected = {'N4LIEF12ref_iteratorIRSt6vectorINS_2PE9RichEntryESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'INFO', 'LOGGING_LEVEL', 'MachO', 'MODES', 'XCODE', 'integrity_error', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF4NoteESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'SPARC', 'GLOBAL', 'OBJECT_TYPES', 'to_json_from_abstract', 'DictStringVersion', 'OAT', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF13SymbolVersionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'MIPS32', 'PPC', 'MCLASS', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_2PE15RelocationEntryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF12ref_iteratorIRSt6vectorINS_2PE6ImportESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'ART', 'Relocation', 'N4LIEF12ref_iteratorISt6vectorIPNS_5MachO10ExportInfoESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF15filter_iteratorISt6vectorIPNS_5MachO6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'to_json', 'V8', 'N4LIEF15filter_iteratorISt6vectorIPNS_3ELF10RelocationESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF12ref_iteratorISt6vectorIPNS_6SymbolESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'ARM64', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF23SymbolVersionDefinitionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_2PE12ResourceNodeESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF12ref_iteratorISt6vectorIPNS_3ELF6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'VERBOSE', 'N4LIEF12ref_iteratorIRKSt6vectorINS_2PE18ResourceDialogItemESaIS3_EEN9__gnu_cxx17__normal_iteratorIPKS3_S5_EEEE', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_5MachO6BinaryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF12DynamicEntryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'is_oat', 'Symbol', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_5MachO6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'is_macho', 'Header', 'parser_error', 'N4LIEF12ref_iteratorIRSt6vectorINS_2PE11ExportEntryESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'N4LIEF12ref_iteratorISt6vectorIPNS_2PE7SectionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'MIPS', 'N4LIEF12ref_iteratorISt6vectorIPNS_5MachO14SegmentCommandESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'not_found', 'MIPS32R6', 'N4LIEF12ref_iteratorISt6vectorIPNS_2PE13DataDirectoryESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'Binary', 'ARM', 'bad_file', 'breakp', 'N4LIEF15filter_iteratorISt6vectorIPNS_3ELF6SymbolESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'exception', 'N4LIEF12ref_iteratorISt6vectorIPNS_7SectionESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'DEBUG', 'MIPS3', 'is_dex', 'ListLangCodeItem', 'UNDEFINED', 'N4LIEF12ref_iteratorISt6vectorIPNS_10RelocationESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'VDEX', 'hash', 'is_pe', 'dex_version', 'oat_version', 'MACHO', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF24SymbolVersionRequirementESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'shell', 'DEX', 'LITTLE', 'Android', 'M32', 'is_art', 'not_supported', 'N4LIEF12ref_iteratorISt6vectorIPNS_5MachO11LoadCommandESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF12ref_iteratorIRSt6vectorINS_2PE6SymbolESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'bad_format', 'N4LIEF12ref_iteratorISt6vectorIPNS_5MachO7SectionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'M64', 'N4LIEF12ref_iteratorIRSt3setIPNS_5MachO10RelocationENS2_6KeyCmpIS3_EESaIS4_EESt23_Rb_tree_const_iteratorIS4_EEE', 'parse', 'MIPSGP64', 'ERROR', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF27SymbolVersionAuxRequirementESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'LIBRARY', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF10RelocationESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'V7', 'is_elf', 'N4LIEF12ref_iteratorIRSt6vectorINS_2PE11ImportEntryESaIS3_EEN9__gnu_cxx17__normal_iteratorIPS3_S5_EEEE', 'OBJECT', 'ARCHITECTURES', 'Logger', 'pe_bad_section_name', 'M16', 'N4LIEF12ref_iteratorISt6vectorIPNS_5MachO12DylibCommandESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'NONE', 'Section', 'FATAL', 'vdex_version', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF16SymbolVersionAuxESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'MIPS64', 'type_error', 'art_version', 'ENDIANNESS', 'N4LIEF12ref_iteratorIRKSt6vectorINS_2PE4x509ESaIS3_EEN9__gnu_cxx17__normal_iteratorIPKS3_S5_EEEE', 'TRACE', 'BIG', 'is_vdex', 'THUMB', 'builder_error', 'SYSZ', 'Object', 'V9', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_2PE10RelocationESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'conversion_error', 'ELF', 'read_out_of_bound', 'pe_error', 'PE', 'WARNING', 'EXE_FORMATS', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF7SectionESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'N4LIEF12ref_iteratorISt6vectorIPNS_5MachO11BindingInfoESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'X86', 'N4LIEF12ref_iteratorIRSt6vectorIPNS_3ELF7SegmentESaIS4_EEN9__gnu_cxx17__normal_iteratorIPS4_S6_EEEE', 'EXECUTABLE', 'UNKNOWN', 'INTEL', 'corrupted', 'not_implemented'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/_pylief.cpython-37m-x86_64-linux-gnu.so', '_pylief', expected)


def test_Crypto_Cipher__XOR():
    expected = {'key_size', 'error', 'new', 'block_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_XOR.cpython-37m-x86_64-linux-gnu.so', '_XOR', expected)


def test_Crypto_Cipher__AES():
    expected = {'key_size', 'MODE_OFB', 'MODE_CTR', 'MODE_ECB', 'MODE_CBC', 'new', 'MODE_PGP', 'MODE_CFB', 'block_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_AES.cpython-37m-x86_64-linux-gnu.so', '_AES', expected)


def test_Crypto_Cipher__Blowfish():
    expected = {'key_size', 'MODE_CFB', 'MODE_PGP', 'MODE_CBC', 'MODE_OFB', 'MODE_CTR', 'MODE_ECB', 'block_size', 'new'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_Blowfish.cpython-37m-x86_64-linux-gnu.so', '_Blowfish', expected)


def test_Crypto_Cipher__ARC4():
    expected = {'key_size', 'block_size', 'error', 'new'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_ARC4.cpython-37m-x86_64-linux-gnu.so', '_ARC4', expected)


def test_Crypto_Cipher__DES():
    expected = {'MODE_CBC', 'MODE_ECB', 'MODE_CTR', 'MODE_CFB', 'MODE_PGP', 'MODE_OFB', 'key_size', 'new', 'block_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_DES.cpython-37m-x86_64-linux-gnu.so', '_DES', expected)


def test_Crypto_Cipher__CAST():
    expected = {'key_size', 'MODE_CTR', 'MODE_CFB', 'block_size', 'MODE_OFB', 'MODE_CBC', 'MODE_PGP', 'MODE_ECB', 'new'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_CAST.cpython-37m-x86_64-linux-gnu.so', '_CAST', expected)


def test_Crypto_Cipher__DES3():
    expected = {'MODE_CBC', 'MODE_CTR', 'MODE_ECB', 'MODE_CFB', 'MODE_OFB', 'key_size', 'block_size', 'new', 'MODE_PGP'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_DES3.cpython-37m-x86_64-linux-gnu.so', '_DES3', expected)


def test_Crypto_Cipher__ARC2():
    expected = {'MODE_CTR', 'MODE_CFB', 'MODE_PGP', 'MODE_OFB', 'block_size', 'key_size', 'new', 'MODE_ECB', 'MODE_CBC'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Cipher/_ARC2.cpython-37m-x86_64-linux-gnu.so', '_ARC2', expected)


def test_Crypto_Util__counter():
    expected = {'_newLE', '_newBE'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Util/_counter.cpython-37m-x86_64-linux-gnu.so', '_counter', expected)


@pytest.mark.xfail(reason="TODO")
def test_Crypto_Util_strxor():
    expected = {'strxor_c', 'strxor'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Util/strxor.cpython-37m-x86_64-linux-gnu.so', 'strxor', expected)


def test_Crypto_Hash__MD4():
    expected = {'digest_size', 'block_size', 'new'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Hash/_MD4.cpython-37m-x86_64-linux-gnu.so', '_MD4', expected)


def test_Crypto_Hash__SHA224():
    expected = {'digest_size', 'new', 'block_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Hash/_SHA224.cpython-37m-x86_64-linux-gnu.so', '_SHA224', expected)


def test_Crypto_Hash__SHA384():
    expected = {'new', 'digest_size', 'block_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Hash/_SHA384.cpython-37m-x86_64-linux-gnu.so', '_SHA384', expected)


def test_Crypto_Hash__RIPEMD160():
    expected = {'new', 'block_size', 'digest_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Hash/_RIPEMD160.cpython-37m-x86_64-linux-gnu.so', '_RIPEMD160', expected)


def test_Crypto_Hash__MD2():
    expected = {'new', 'digest_size', 'block_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Hash/_MD2.cpython-37m-x86_64-linux-gnu.so', '_MD2', expected)


def test_Crypto_Hash__SHA512():
    expected = {'block_size', 'digest_size', 'new'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Hash/_SHA512.cpython-37m-x86_64-linux-gnu.so', '_SHA512', expected)


def test_Crypto_Hash__SHA256():
    expected = {'new', 'block_size', 'digest_size'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/Crypto/Hash/_SHA256.cpython-37m-x86_64-linux-gnu.so', '_SHA256', expected)


def test_typed_ast__ast27():
    expected = {'List', 'Index', 'Pass', 'ListComp', 'Str', 'arguments', 'Del', 'For', 'LShift', 'In', 'BitOr', 'parse', 'NotEq', 'cmpop', 'Or', 'Param', 'SetComp', 'With', 'comprehension', 'Repr', 'Assert', 'Tuple', 'Interactive', 'Ellipsis', 'BinOp', 'Lambda', 'And', 'Num', 'boolop', 'stmt', 'Eq', 'unaryop', 'Assign', 'TryExcept', 'BitAnd', 'BitXor', 'operator', 'ExceptHandler', 'AugLoad', 'Expression', 'Div', 'Name', 'Attribute', 'Break', 'AST', 'Slice', 'Suite', 'mod', 'Call', 'LtE', 'Invert', 'USub', 'keyword', 'slice', 'PyCF_ONLY_AST', 'FunctionDef', 'Load', 'TryFinally', 'AugStore', 'Return', 'Raise', 'ExtSlice', 'Set', 'Sub', 'Expr', 'Import', 'Not', 'UAdd', 'GeneratorExp', 'Yield', 'Dict', 'FunctionType', 'excepthandler', 'Continue', 'IfExp', 'FloorDiv', 'NotIn', 'Pow', 'UnaryOp', 'RShift', 'Module', 'DictComp', 'IsNot', 'Print', 'ClassDef', 'Compare', 'expr', 'Subscript', 'Add', 'Global', 'GtE', 'type_ignore', 'Mod', 'TypeIgnore', 'While', 'expr_context', 'Store', 'BoolOp', 'Is', 'ImportFrom', 'Gt', 'alias', 'Exec', 'If', 'Lt', 'Mult', 'Delete', 'AugAssign'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/typed_ast/_ast27.cpython-37m-x86_64-linux-gnu.so', '_ast27', expected)


def test_typed_ast__ast3():
    expected = {'Suite', 'Assign', 'PyCF_ONLY_AST', 'YieldFrom', 'Module', 'For', 'type_ignore', 'Assert', 'keyword', 'Raise', 'In', 'Lt', 'alias', 'LShift', 'Ellipsis', 'slice', 'And', 'Continue', 'arg', 'Mult', 'Tuple', 'Name', 'FloorDiv', 'DictComp', 'AugAssign', 'Add', 'ExtSlice', 'NotIn', 'mod', 'Await', 'RShift', 'Del', 'Interactive', 'withitem', 'Nonlocal', 'GtE', 'Lambda', 'While', 'Attribute', 'unaryop', 'Not', 'ListComp', 'FormattedValue', 'Yield', 'Gt', 'Mod', 'Call', 'Sub', 'Pow', 'Global', 'Store', 'boolop', 'ExceptHandler', 'AsyncFunctionDef', 'Try', 'ImportFrom', 'MatMult', 'Param', 'excepthandler', 'BitAnd', 'BitXor', 'operator', 'comprehension', 'ClassDef', 'arguments', 'expr_context', 'Set', 'AugStore', 'LtE', 'IsNot', 'Dict', 'BoolOp', '_parse', 'JoinedStr', 'Expr', 'List', 'Slice', 'USub', 'Constant', 'SetComp', 'FunctionDef', 'BitOr', 'AnnAssign', 'Index', 'TypeIgnore', 'Bytes', 'AugLoad', 'UAdd', 'Is', 'expr', 'With', 'Or', 'Pass', 'Div', 'UnaryOp', 'Compare', 'FunctionType', 'NotEq', 'Num', 'If', 'IfExp', 'Break', 'NameConstant', 'Starred', 'Delete', 'AsyncFor', 'AsyncWith', 'stmt', 'AST', 'Invert', 'Eq', 'Subscript', 'GeneratorExp', 'Str', 'BinOp', 'Load', 'Return', 'Import', 'Expression', 'cmpop'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/typed_ast/_ast3.cpython-37m-x86_64-linux-gnu.so', '_ast3', expected)


def test__scrypt():
    expected = set()
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/_scrypt.cpython-37m-x86_64-linux-gnu.so', '_scrypt', expected)


@pytest.mark.xfail(reason="TODO")
def test__cffi_backend():
    expected = {'set_errno', 'RTLD_DEEPBIND', 'from_buffer', 'gcp', '_init_cffi_1_0_external_module', 'get_errno', 'typeoffsetof', 'unpack', 'RTLD_LAZY', '_C_API', 'cast', 'sizeof', 'new_struct_type', 'new_primitive_type', 'new_function_type', 'release', 'RTLD_GLOBAL', 'new_pointer_type', 'newp', 'typeof', 'FFI_CDECL', 'string', 'callback', 'Lib', 'new_union_type', 'buffer', 'new_enum_type', 'memmove', '_testfunc', 'load_library', 'getcname', '_get_types', 'newp_handle', 'RTLD_LOCAL', 'new_array_type', 'RTLD_NODELETE', '_testbuff', 'from_handle', 'alignof', 'complete_struct_or_union', 'FFI_DEFAULT_ABI', 'FFI', 'rawaddressof', 'RTLD_NOLOAD', 'new_void_type', '_get_common_types', 'RTLD_NOW'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/_cffi_backend.cpython-37m-x86_64-linux-gnu.so', '_cffi_backend', expected)


def test_wrapt__wrappers():
    expected = {'BoundFunctionWrapper', 'CallableObjectProxy', 'ObjectProxy', '_FunctionWrapperBase', 'PartialCallableObjectProxy', 'FunctionWrapper'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/wrapt/_wrappers.cpython-37m-x86_64-linux-gnu.so', '_wrappers', expected)


def test_psutil__psutil_linux():
    expected = {'set_testing', 'proc_cpu_affinity_set', 'proc_ioprio_set', 'version', 'users', 'DUPLEX_FULL', 'DUPLEX_HALF', 'net_if_duplex_speed', 'linux_sysinfo', 'DUPLEX_UNKNOWN', 'proc_ioprio_get', 'disk_partitions', 'proc_cpu_affinity_get'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/psutil/_psutil_linux.cpython-37m-x86_64-linux-gnu.so', '_psutil_linux', expected)


def test_psutil__psutil_posix():
    expected = {'setpriority', 'net_if_flags', 'net_if_addrs', 'net_if_mtu', 'getpriority'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/psutil/_psutil_posix.cpython-37m-x86_64-linux-gnu.so', '_psutil_posix', expected)


def test_mamba_mamba_api():
    pytest.skip("Something is very wrong with this test")
    expected = {'SOLVER_SOLVABLE', 'Transaction', 'SOLVER_FLAG_SPLITPROVIDES', 'SOLVER_FLAG_NEED_UPDATEPROVIDE', 'SOLVER_FLAG_BEST_OBEY_POLICY', 'SOLVER_NOAUTOSET', 'SOLVER_NOTBYUSER', 'calculate_channel_urls', 'SOLVER_DISFAVOR', 'SOLVER_ORUPDATE', 'SOLVER_FLAG_IGNORE_RECOMMENDED', 'SOLVER_FLAG_FOCUS_BEST', 'Repo', 'SOLVER_JOBMASK', 'SOLVER_TARGETED', 'SOLVER_WEAKENDEPS', 'SOLVER_NOOP', 'SOLVER_SOLVABLE_ONE_OF', 'SOLVER_FLAG_KEEP_ORPHANS', 'SOLVER_ERASE', 'SOLVER_SOLVABLE_PROVIDES', 'SOLVER_CLEANDEPS', 'SOLVER_FLAG_ALLOW_UNINSTALL', 'SOLVER_SELECTMASK', 'SOLVER_FLAG_DUP_ALLOW_ARCHCHANGE', 'PrefixData', 'Context', 'SOLVER_FLAG_ALLOW_ARCHCHANGE', 'SOLVER_LOCK', 'SubdirData', 'Channel', 'MAMBA_FORCE_REINSTALL', 'QueryFormat', 'SOLVER_FLAG_BREAK_ORPHANS', 'SOLVER_FLAG_KEEP_EXPLICIT_OBSOLETES', 'SOLVER_FLAG_ALLOW_DOWNGRADE', 'SOLVER_FLAG_NO_INFARCHCHECK', 'Path', 'DownloadTargetList', 'SOLVER_FLAG_DUP_ALLOW_VENDORCHANGE', 'SOLVER_SETEV', 'SOLVER_SETREPO', 'SOLVER_SETEVR', 'SOLVER_FLAG_FOCUS_INSTALLED', 'SOLVER_FLAG_DUP_ALLOW_DOWNGRADE', 'SOLVER_FLAG_NO_AUTOTARGET', 'SOLVER_WEAK', 'SOLVER_USERINSTALLED', 'SOLVER_FLAG_YUM_OBSOLETES', 'SOLVER_SETNAME', 'SOLVER_FLAG_STRONG_RECOMMENDS', 'Solver', 'Query', 'SOLVER_ALLOWUNINSTALL', 'get_channel_urls', 'SOLVER_FLAG_ALLOW_NAMECHANGE', 'SOLVER_SOLVABLE_REPO', 'SOLVER_SOLVABLE_NAME', 'cache_fn_url', 'create_cache_dir', 'SOLVER_ESSENTIAL', 'SOLVER_FLAG_URPM_REORDER', 'SOLVER_SETMASK', 'SOLVER_SETARCH', 'SOLVER_FLAG_NO_UPDATEPROVIDE', 'SOLVER_FLAG_ADD_ALREADY_RECOMMENDED', 'SOLVER_DROP_ORPHANED', 'Pool', 'SOLVER_FORCEBEST', 'MultiPackageCache', 'SOLVER_FLAG_DUP_ALLOW_NAMECHANGE', 'SOLVER_FLAG_ALLOW_VENDORCHANGE', 'SOLVER_DISTUPGRADE', 'SOLVER_SOLVABLE_ALL', 'transmute', 'SOLVER_MULTIVERSION', 'SOLVER_UPDATE', 'SOLVER_FLAG_INSTALL_ALSO_UPDATES', 'MambaNativeException', 'SOLVER_SETVENDOR', 'SOLVER_FLAG_ONLY_NAMESPACE_RECOMMENDED', 'SOLVER_VERIFY', 'MAMBA_NO_DEPS', 'SOLVER_INSTALL', 'SOLVER_FAVOR', 'MAMBA_ONLY_DEPS'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/mamba/mamba_api.cpython-37m-x86_64-linux-gnu.so', 'mamba_api', expected)


def test_editdistance_bycython():
    expected = {'eval'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/editdistance/bycython.cpython-37m-x86_64-linux-gnu.so', 'bycython', expected)


def test_aiohttp__http_writer():
    expected = {'istr', '_serialize_headers'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/aiohttp/_http_writer.cpython-37m-x86_64-linux-gnu.so', '_http_writer', expected, xmissing=True)


def test_aiohttp__frozenlist():
    expected = {'MutableSequence', 'FrozenList', '__pyx_unpickle_FrozenList'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/aiohttp/_frozenlist.cpython-37m-x86_64-linux-gnu.so', '_frozenlist', expected, xmissing=True)


def test_aiohttp__helpers():
    expected = {'__pyx_unpickle_reify', 'reify'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/aiohttp/_helpers.cpython-37m-x86_64-linux-gnu.so', '_helpers', expected, xmissing=True)


def test_aiohttp__http_parser():
    expected = {'_DeflateBuffer', 'BadHttpMessage', '__pyx_unpickle_RawResponseMessage', 'BadStatusLine', 'hdrs', 'HttpResponseParser', 'LineTooLong', 'PayloadEncodingError', 'parse_url', 'TransferEncodingError', 'ContentLengthError', '_URL', '__pyx_unpickle_RawRequestMessage', 'HttpRequestParser', '_CIMultiDictProxy', '_HttpVersion', '_HttpVersion11', '_StreamReader', '_HttpVersion10', 'InvalidHeader', 'InvalidURLError', '_EMPTY_PAYLOAD', 'RawResponseMessage', 'i', 'RawRequestMessage', '_CIMultiDict'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/aiohttp/_http_parser.cpython-37m-x86_64-linux-gnu.so', '_http_parser', expected, xmissing=True)


def test_aiohttp__websocket():
    expected = {'_websocket_mask_cython'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/aiohttp/_websocket.cpython-37m-x86_64-linux-gnu.so', '_websocket', expected, xmissing=True)


def test_multidict__multidict():
    expected = {'CIMultiDict', 'MultiDict', 'MultiDictProxy', 'getversion', 'istr', 'CIMultiDictProxy'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/multidict/_multidict.cpython-37m-x86_64-linux-gnu.so', '_multidict', expected)


def test_ruamel_yaml_ext__ruamel_yaml():
    expected = {'ScalarToken', 'MappingNode', 'SequenceEndEvent', 'ScannerError', 'BlockEntryToken', 'ConstructorError', 'YAMLError', 'ComposerError', 'FlowSequenceEndToken', 'DocumentStartEvent', 'StreamEndToken', 'TagToken', 'ScalarNode', 'SequenceStartEvent', 'MappingEndEvent', 'FlowMappingStartToken', 'MappingStartEvent', 'CEmitter', 'get_version_string', 'BlockEndToken', 'StreamStartEvent', 'EmitterError', 'get_version', '__pyx_unpickle_Mark', 'ReaderError', 'Mark', 'DocumentStartToken', 'DocumentEndToken', 'StreamEndEvent', 'AliasToken', 'DirectiveToken', 'FlowEntryToken', 'BlockMappingStartToken', 'FlowSequenceStartToken', 'ValueToken', 'AliasEvent', 'KeyToken', 'BlockSequenceStartToken', 'CParser', 'FlowMappingEndToken', 'AnchorToken', 'DocumentEndEvent', 'ParserError', 'SerializerError', 'StreamStartToken', 'SequenceNode', 'RepresenterError', 'ScalarEvent'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/ruamel_yaml/ext/_ruamel_yaml.cpython-37m-x86_64-linux-gnu.so', '_ruamel_yaml', expected, xmissing=True)


def test_conda_package_handling_archive_utils_cy():
    expected = {'extract_file', 'create_archive'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/conda_package_handling/archive_utils_cy.cpython-37m-x86_64-linux-gnu.so', 'archive_utils_cy', expected, xmissing=True)


def test_pvectorc():
    expected = {'pvector', 'PVector'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/pvectorc.cpython-37m-x86_64-linux-gnu.so', 'pvectorc', expected)


def test_yarl__quoting_c():
    expected = {'_Quoter', '_Unquoter', 'i', 'digits', 'ascii_letters', '__pyx_unpickle__Quoter', '__pyx_unpickle__Unquoter'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/yarl/_quoting_c.cpython-37m-x86_64-linux-gnu.so', '_quoting_c', expected, xmissing=True)


def test__ruamel_yaml():
    expected = {'FlowMappingEndToken', 'YAMLError', 'ScalarNode', 'CEmitter', 'MappingStartEvent', 'DocumentEndToken', 'StreamStartEvent', 'SerializerError', 'ValueToken', 'StreamStartToken', 'EmitterError', 'RepresenterError', 'Mark', 'AliasToken', 'MappingEndEvent', 'SequenceEndEvent', 'FlowEntryToken', 'ParserError', 'BlockEntryToken', 'AnchorToken', 'BlockSequenceStartToken', 'SequenceStartEvent', 'DocumentEndEvent', 'FlowSequenceEndToken', 'FlowMappingStartToken', 'get_version_string', 'ScannerError', '__pyx_unpickle_Mark', 'KeyToken', 'TagToken', 'CParser', 'ConstructorError', 'ScalarEvent', 'AliasEvent', 'ComposerError', 'BlockEndToken', 'DocumentStartToken', 'BlockMappingStartToken', 'FlowSequenceStartToken', 'get_version', 'StreamEndEvent', 'StreamEndToken', 'ReaderError', 'SequenceNode', 'MappingNode', 'ScalarToken', 'DocumentStartEvent', 'DirectiveToken'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/_ruamel_yaml.cpython-37m-x86_64-linux-gnu.so', '_ruamel_yaml', expected, xmissing=True)


def test_coverage_tracer():
    expected = {'CFileDisposition', 'CTracer'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/coverage/tracer.cpython-37m-x86_64-linux-gnu.so', 'tracer', expected)


def test_lazy_object_proxy_cext():
    expected = {'identity', 'Proxy'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/lazy_object_proxy/cext.cpython-37m-x86_64-linux-gnu.so', 'cext', expected)


def test_pycosat():
    expected = {'__version__', 'itersolve', 'solve'}
    compare('/home/cburr/miniconda3/lib/python3.7/site-packages/pycosat.cpython-37m-x86_64-linux-gnu.so', 'pycosat', expected)
