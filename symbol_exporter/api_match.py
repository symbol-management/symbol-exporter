"""tools for matching the volumes with artifacts that supply the symbols"""
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from itertools import groupby

from symbol_exporter.ast_symbol_extractor import builtin_symbols
from symbol_exporter.db_access_model import WebDB

web_interface = WebDB()


def recursive_get_from_table(symbol, get_symbol_table_func=web_interface.get_symbol_table, seen_symbols=set()):
    output_supply = {}
    parent_symbol = symbol
    children_symbols = []
    seen_symbols = seen_symbols.union({symbol})
    symbol_table = get_symbol_table_func(parent_symbol.partition(".")[0])
    while parent_symbol:
        supply = symbol_table.get("symbol table", {}).get(parent_symbol)
        if supply is None:
            if "." not in parent_symbol:
                break
            parent_symbol, _, child_symbol = parent_symbol.rpartition(".")
            children_symbols.append(child_symbol)
        else:
            for suplier in supply:
                shadow = suplier.get("shadows")
                if shadow:
                    new_symbol = ".".join([shadow] + list(reversed(children_symbols)))
                    # TODO: handle this in a special manner since this is a grey area, it could hide deps we don't see
                    #  but nominally would be covered by the dependency's own dependency spec
                    if new_symbol in seen_symbols:
                        output_supply.setdefault(parent_symbol, []).append(suplier["artifact name"])
                        continue
                    rescursive_search_results = recursive_get_from_table(
                        new_symbol, get_symbol_table_func, seen_symbols
                    )
                    if rescursive_search_results:
                        output_supply.setdefault(parent_symbol, []).append(suplier["artifact name"])
                        output_supply.update(rescursive_search_results)
                # If not a shadows then we must have the full symbol
                elif not children_symbols:
                    output_supply.setdefault(parent_symbol, []).append(suplier["artifact name"])
            break

    return output_supply


def find_supplying_version_set(volume, get_symbol_table_func=web_interface.get_symbol_table):
    effective_volume = sorted(volume - builtin_symbols)
    supplies = {}
    bad_symbols = set()
    for v_symbol in effective_volume:
        supply = recursive_get_from_table(v_symbol, get_symbol_table_func)
        if not supply:
            bad_symbols.add(v_symbol)
            continue
        for symbol, artifacts in supply.items():
            top_level_symbol = symbol.partition(".")[0]
            if top_level_symbol not in supplies:
                supplies[top_level_symbol] = set(artifacts)
            else:
                supplies[top_level_symbol] &= set(artifacts)
    return supplies or {}, bad_symbols


def extract_artifacts_from_deps(deps):
    # TODO: places where multiple artifacts from different packages
    # satisfy (eg backport pkgs, google-requests error, etc)
    versions_by_package = {}
    for import_name, artifacts in deps.items():
        version_set = set()
        if not artifacts:
            continue
        for artifact_path in artifacts:
            package_name, channel, arch, artifact = artifact_path.split("/")
            artifact_name, version, build_string = artifact.rsplit("-", 3)
            version_set.add(version)
        if package_name not in versions_by_package:
            versions_by_package[package_name] = version_set
        else:
            versions_by_package[package_name] &= versions_by_package[package_name]
    return versions_by_package
