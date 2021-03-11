from itertools import groupby

import requests

from symbol_exporter.ast_symbol_extractor import builtin_symbols, version

host = "https://cf-ast-symbol-table.web.cern.ch"


def get_symbol_table(top_level_import):
    symbol_table_url = f"/api/v{version}/symbol_table/{top_level_import}"
    # TODO: pull io up/out? Or run in parallel or cache?
    request = requests.get(f"{host}{symbol_table_url}")
    if request.status_code != 200:
        return {}
    return request.json()['symbol table']


def find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table):
    supplying_versions = {}

    symbol_by_top_level = groupby(
        sorted(volume - builtin_symbols), key=lambda x: x.partition(".")[0]
    )

    bad_symbols = set()

    for top_level_import, v_symbols in symbol_by_top_level:
        symbol_table = get_symbol_table_func(top_level_import)
        # TODO: handle star imports recursion here?
        for v_symbol in v_symbols:
            supply = symbol_table.get(v_symbol)
            if not supply:
                bad_symbols.add(v_symbol)
                continue
            supplying_versions.setdefault(top_level_import, list()).append(set(supply))
    # TODO: handle the case where multiple pkgs export the same symbols?
    #  In that case we may want to merge thsoe together somehow
    # TODO: handle case where no pkg supports the symbol?
    return [set.intersection(*v) for v in supplying_versions.values()], bad_symbols
