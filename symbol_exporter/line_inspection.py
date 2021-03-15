from symbol_exporter.ast_index import get_symbol_table
from symbol_exporter.ast_symbol_extractor import SymbolType, builtin_symbols


def infer_filenames(module_symbols):
    out = {}
    for i, symbol in enumerate(module_symbols):
        z = module_symbols.pop(i)
        if any(m.startswith(z) for m in module_symbols):
            out[z] = z.replace(".", "/") + "__init__.py"
        else:
            out[z] = z.replace(".", "/") + ".py"
        module_symbols.insert(i, z)
    return out


def munge_artifacts(artifacts):
    out = []
    for artifact in set(artifacts) - {"*"}:
        fn = artifact.rsplit("/", 1)[-1]
        name, version, _ = fn.rsplit("-", 2)
        out.append((name, version))
    return out


def line_inspection(symbols, pkg_environment):
    bad_lines = []
    module_symbols = [s for s in symbols if symbols[s]["type"] == SymbolType.MODULE]
    filename_by_module = infer_filenames(module_symbols)
    for symbol, md in symbols.items():
        module_name = symbol
        while True:
            filename = filename_by_module.get(module_name)
            if filename:
                break
            else:
                module_name = module_name.rsplit(".", 1)[0]
        volume = md.get("data", {}).get("symbols_in_volume", {})
        for volume_symbol in set(volume) - builtin_symbols:
            # dereference shadows
            effective_volume_symbol = (
                symbols.get(volume_symbol, {})
                .get("data", {})
                .get("shadows", volume_symbol)
            )
            # don't bother with our own symbols
            if effective_volume_symbol in symbols:
                continue
            # get symbol table
            symbol_table = get_symbol_table(
                effective_volume_symbol.partition(".")[0]
            ).get("symbol table", {})
            supplying_pkgs = munge_artifacts(
                symbol_table.get(effective_volume_symbol, [])
            )
            # for each symbol in the group check if overlap between pkg_environment and table
            symbol_in_env = set(pkg_environment) & set(supplying_pkgs)
            # for those that aren't in pkg env note the line and symbol
            if not symbol_in_env:
                bad_lines.append(
                    (
                        filename,
                        volume[volume_symbol]["line number"],
                        effective_volume_symbol,
                    )
                )
    return bad_lines
