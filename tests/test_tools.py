from conda.models.version import VersionSpec

from symbol_exporter.tools import find_version_ranges


def check_result(all_versions, acceptable_versions, expected_range):
    version_ranges = find_version_ranges(all_versions, acceptable_versions)
    assert expected_range == version_ranges
    if expected_range:
        specifier = VersionSpec(expected_range)
        assert all(specifier.any_match(v) for v in acceptable_versions)


def test_all_versions_acceptable():
    check_result(["1.0", "1.1", "1.1.1"], ["1.0", "1.1", "1.1.1"], ">=1.0,<=1.1.1")


def test_some_versions_acceptable():
    check_result(["1.0", "1.1", "1.1.1", "1.1.2"], ["1.0", "1.1", "1.1.1"], ">=1.0,<=1.1.1")


def test_versions_acceptable_with_island():
    check_result(["1.0", "1.1", "1.1.1", "1.1.2", "1.1.3"], ["1.0", "1.1", "1.1.1", "1.1.3"], ">=1.0,<=1.1.1|1.1.3")


def test_versions_acceptable_with_two_ranges():
    check_result(
        ["1.0", "1.1", "1.1.1", "1.1.2", "1.1.3", "1.1.4"],
        ["1.0", "1.1", "1.1.1", "1.1.3", "1.1.4"],
        ">=1.0,<=1.1.1|>=1.1.3,<=1.1.4",
    )


def test_versions_acceptable_with_two_islands():
    check_result(
        ["1.0", "1.1", "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5"],
        ["1.0", "1.1", "1.1.1", "1.1.3", "1.1.5"],
        ">=1.0,<=1.1.1|1.1.3|1.1.5",
    )


def test_versions_acceptable_with_no_compatible():
    check_result(["1.0", "1.1", "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5"], [], "")
