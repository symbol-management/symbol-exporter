from itertools import groupby

import requests
from libcflib.jsonutils import loads

FILE_LISTING_URL = "https://raw.githubusercontent.com/symbol-management/ast-symbol-table/master/.file_listing.json"

RAW_URL_TEMPLATE = "https://raw.githubusercontent.com/symbol-management/ast-symbol-table/master/{}.json"


def get_symbol_table(top_level_import):
    url = RAW_URL_TEMPLATE.format(top_level_import)
    # TODO: pull io up/out? Or run in parallel or cache?
    return loads(requests.get(url).text)


def find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table):
    supplying_versions = {}

    symbol_by_top_level = groupby(volume, key=lambda x: x.partition(".")[0])

    for top_level_import, v_symbols in symbol_by_top_level:
        symbol_table = get_symbol_table_func(top_level_import)
        # TODO: handle star imports recursion here?
        for v_symbol in v_symbols:
            supply = symbol_table.get(v_symbol)
            supplying_versions.setdefault(top_level_import, list()).append(supply)
    # TODO: handle the case where multiple pkgs export the same symbols?
    #  In that case we may want to merge thsoe together somehow
    return [set.intersection(*v) for v in supplying_versions.values()]
