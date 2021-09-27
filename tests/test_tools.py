from symbol_exporter.tools import find_version_ranges


def test_all_versions_acceptable():
    assert find_version_ranges(['1.0', '1.1', '1.1.1'], ['1.0', '1.1', '1.1.1']) == '>=1.0,<=1.1.1'

def test_some_versions_acceptable():
    assert find_version_ranges(['1.0', '1.1', '1.1.1', '1.1.2'], ['1.0', '1.1', '1.1.1']) == '>=1.0,<=1.1.1'

def test_versions_acceptable_with_island():
    assert find_version_ranges(['1.0', '1.1', '1.1.1', '1.1.2', '1.1.3'], ['1.0', '1.1', '1.1.1', '1.1.3']) == '>=1.0,<=1.1.1,1.1.3'

def test_versions_acceptable_with_two_ranges():
    assert find_version_ranges(['1.0', '1.1', '1.1.1', '1.1.2', '1.1.3', '1.1.4'], ['1.0', '1.1', '1.1.1', '1.1.3', '1.1.4']) == '>=1.0,<=1.1.1,>=1.1.3,<=1.1.4'

def test_versions_acceptable_with_two_islands():
    assert find_version_ranges(['1.0', '1.1', '1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1.5'], 
    ['1.0', '1.1', '1.1.1', '1.1.3', '1.1.5']) == '>=1.0,<=1.1.1,1.1.3,1.1.5'

def test_versions_acceptable_with_no_compatible():
    assert find_version_ranges(['1.0', '1.1', '1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1.5'], []) == ''