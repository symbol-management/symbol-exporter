import requests
from libcflib.jsonutils import loads

FILE_LISTING_URL = 'https://raw.githubusercontent.com/symbol-management/ast-symbol-table/master/.file_listing.json'

RAW_URL_TEMPLATE = 'https://raw.githubusercontent.com/symbol-management/ast-symbol-table/master/{}.json'


def find_supplying_version_set(symbols):
    volume = set()
    for k, v in symbols.items():
        volume.update(v['symbols_in_volume'])

    supplying_versions = []
    symbol_by_top_level = {}

    # TODO: handle with groupby
    for v_symbol in volume:
        top_level_import = v_symbol.partition('.')[0]
        symbol_by_top_level.setdefault(top_level_import, set()).add(v_symbol)

    for top_level_import, v_symbols in symbol_by_top_level.items():
        url = RAW_URL_TEMPLATE.format(top_level_import)
        # TODO: pull io up/out? Or run in parallel
        symbol_table = loads(requests.get(url).text)

        # TODO: handle star imports recursion here?
        for v_symbol in v_symbols:
            supply = symbol_table.get(v_symbol)
            if not supply:
                return set()
            supplying_versions.append(supply)
    return set.intersection(*supplying_versions)
