"""tools for matching the volumes with artifacts that supply the symbols"""
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from itertools import groupby

from symbol_exporter.ast_symbol_extractor import builtin_symbols
from symbol_exporter.db_access_model import WebDB

web_interface = WebDB()


def get_supply(top_level_import, v_symbols, get_symbol_table_func=web_interface.get_symbol_table):
    supplies = None
    bad_symbols = set()
    symbol_table = get_symbol_table_func(top_level_import).get('symbol table', {})
    # TODO: handle star imports recursion here?
    for v_symbol in v_symbols:
        supply = symbol_table.get(v_symbol)
        if not supply:
            bad_symbols.add(v_symbol)
            continue
        if supplies is None:
            supplies = set(supply)
        else:
            supplies &= set(supply)
    return supplies or set(), bad_symbols


def find_supplying_version_set(volume, get_symbol_table_func=web_interface.get_symbol_table):
    supplying_versions = {}

    effective_volume = sorted(volume - builtin_symbols)
    symbol_by_top_level = groupby(effective_volume, key=lambda x: x.partition(".")[0])
    bad_symbols = set()

    with ThreadPoolExecutor() as pool:
        futures = {
            pool.submit(get_supply, top_level_import, list(v_symbols), get_symbol_table_func): top_level_import
            for top_level_import, v_symbols in symbol_by_top_level
        }
    for future in as_completed(futures):
        top_level_import = futures[future]
        supplies, bad = future.result()
        supplying_versions[top_level_import] = supplies
        bad_symbols.update(bad)
    # TODO: handle the case where multiple pkgs export the same symbols?
    #  In that case we may want to merge those together somehow
    # TODO: handle case where no pkg supports the symbol?
    return supplying_versions, bad_symbols
