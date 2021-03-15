from symbol_exporter.ast_symbol_extractor import SymbolType
from symbol_exporter.line_inspection import line_inspection


def test_line_inspection():
    symbols = {
        "z": {
            "data": {"symbols_in_volume": "requests.ConnectTimeout"},
            "type": SymbolType.FUNCTION,
        }
    }
    env = []
    actual = line_inspection(symbols, env)
    assert set(actual) & {("requests", "2.25.1")}
