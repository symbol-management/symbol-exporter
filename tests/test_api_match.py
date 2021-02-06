from symbol_exporter.api_match import find_supplying_version_set

SAMPLE_TABLE = {
    "academic.cli": {
        "academic-0.2.8-py_0",
        "academic-0.3.0-py_0",
        "academic-0.3.1-py_0",
        "academic-0.4.0-py_0",
        "academic-0.5.0-py_0",
        "academic-0.5.1-py_0",
        "academic-0.6.1-py_0",
        "academic-0.6.2-py_0",
        "academic-0.7.0-py_0",
    },
    "academic.cli.AcademicError": {
        "academic-0.5.1-py_0",
        "academic-0.6.1-py_0",
        "academic-0.6.2-py_0",
        "academic-0.7.0-py_0",
    },
    "academic.cli.clean_bibtex_authors": {
        "academic-0.2.8-py_0",
        "academic-0.3.0-py_0",
        "academic-0.3.1-py_0",
        "academic-0.4.0-py_0",
        "academic-0.5.0-py_0",
    },
    "zappy": {"zappy-0.1.0-py_0", "zappy-0.2.0-py_0"},
}


def test_find_supplying_version_set():
    volume = {"academic.cli", "academic.cli.AcademicError"}

    intersection = find_supplying_version_set(
        volume, get_symbol_table_func=lambda x: SAMPLE_TABLE
    )
    assert intersection == [
        {
            "academic-0.5.1-py_0",
            "academic-0.6.1-py_0",
            "academic-0.6.2-py_0",
            "academic-0.7.0-py_0",
        }
    ]


def test_find_supplying_version_multi_pkg_set():
    volume = {"academic.cli", "academic.cli.AcademicError", "zappy"}

    intersection = find_supplying_version_set(
        volume, get_symbol_table_func=lambda x: SAMPLE_TABLE
    )
    assert intersection == [
        {
            "academic-0.5.1-py_0",
            "academic-0.6.1-py_0",
            "academic-0.6.2-py_0",
            "academic-0.7.0-py_0",
        },
        {"zappy-0.1.0-py_0", "zappy-0.2.0-py_0"},
    ]


def test_find_supplying_version_null_set():
    volume = {
        "academic.cli",
        "academic.cli.AcademicError",
        "academic.cli.clean_bibtex_authors",
    }

    intersection = find_supplying_version_set(
        volume, get_symbol_table_func=lambda x: SAMPLE_TABLE
    )
    assert intersection == [set()]
