from symbol_exporter.api_match import find_supplying_version_set, recursive_get_from_table

SAMPLE_TABLE = {
    "academic": {
        "academic.cli": [
            {"artifact name": "academic-0.2.8-py_0"},
            {"artifact name": "academic-0.3.0-py_0"},
            {"artifact name": "academic-0.3.1-py_0"},
            {"artifact name": "academic-0.4.0-py_0"},
            {"artifact name": "academic-0.5.0-py_0"},
            {"artifact name": "academic-0.5.1-py_0"},
            {"artifact name": "academic-0.6.1-py_0"},
            {"artifact name": "academic-0.6.2-py_0"},
            {"artifact name": "academic-0.7.0-py_0"},
        ],
        "academic.cli.AcademicError": [
            {"artifact name": "academic-0.5.1-py_0"},
            {"artifact name": "academic-0.6.1-py_0"},
            {"artifact name": "academic-0.6.2-py_0"},
            {"artifact name": "academic-0.7.0-py_0"},
        ],
        "academic.cli.clean_bibtex_authors": [
            {"artifact name": "academic-0.2.8-py_0"},
            {"artifact name": "academic-0.3.0-py_0"},
            {"artifact name": "academic-0.3.1-py_0"},
            {"artifact name": "academic-0.4.0-py_0"},
            {"artifact name": "academic-0.5.0-py_0"},
        ],
    },
    "zappy": {
        "zappy": [
            {"artifact name": "zappy-0.1.0-py_0"},
            {"artifact name": "zappy-0.2.0-py_0"},
            {"artifact name": "fork-zappy-0.2.0-py_0"},
        ]
    },
    "shadow_academic": {
        "shadow_academic": [
            {"artifact name": "shadow_academic-0.0.1", "shadows": "academic"},
            {"artifact name": "shadow_academic-0.0.2", "shadows": "academic"},
        ]
    },
    "cchardet": {
        "cchardet": [{"artifact name": "cchardet/conda-forge/linux-64/cchardet-2.1.1-py27_0"}],
        "cchardet._cchardet": [
            {"artifact name": "cchardet/conda-forge/linux-64/cchardet-2.1.1-py27_0", "shadows": "cchardet._cchardet"}
        ],
    },
}


def get_symbol_table_dummy_func(x):
    return {"symbol table": SAMPLE_TABLE.get(x, {}), "metadata": {}}


def test_find_supplying_version_set():
    volume = {"academic.cli", "academic.cli.AcademicError"}

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == {
        "academic": {
            "academic-0.5.1-py_0",
            "academic-0.6.1-py_0",
            "academic-0.6.2-py_0",
            "academic-0.7.0-py_0",
        }
    }


def test_find_supplying_version_multi_pkg_set():
    volume = {"academic.cli", "academic.cli.AcademicError", "zappy"}

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == {
        "academic": {
            "academic-0.5.1-py_0",
            "academic-0.6.1-py_0",
            "academic-0.6.2-py_0",
            "academic-0.7.0-py_0",
        },
        "zappy": {"zappy-0.1.0-py_0", "zappy-0.2.0-py_0", "fork-zappy-0.2.0-py_0"},
    }


def test_find_supplying_version_null_set():
    volume = {
        "academic.cli",
        "academic.cli.AcademicError",
        "academic.cli.clean_bibtex_authors",
    }

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == {"academic": set()}


def test_find_supplying_version_set_shadows():
    volume = {"shadow_academic.cli", "shadow_academic.cli.AcademicError"}

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == {
        "shadow_academic": {"shadow_academic-0.0.1", "shadow_academic-0.0.2"},
        "academic": {
            "academic-0.5.1-py_0",
            "academic-0.6.1-py_0",
            "academic-0.6.2-py_0",
            "academic-0.7.0-py_0",
        },
    }


def test_recursive_get_from_table():
    intersection = recursive_get_from_table(
        "academic.cli.AcademicError", get_symbol_table_func=get_symbol_table_dummy_func
    )
    assert intersection == {
        "academic.cli.AcademicError": [
            "academic-0.5.1-py_0",
            "academic-0.6.1-py_0",
            "academic-0.6.2-py_0",
            "academic-0.7.0-py_0",
        ]
    }


def test_recursive_get_from_table_shadows():
    intersection = recursive_get_from_table(
        "shadow_academic.cli.AcademicError", get_symbol_table_func=get_symbol_table_dummy_func
    )
    assert intersection == {
        "shadow_academic": ["shadow_academic-0.0.1", "shadow_academic-0.0.2"],
        "academic.cli.AcademicError": [
            "academic-0.5.1-py_0",
            "academic-0.6.1-py_0",
            "academic-0.6.2-py_0",
            "academic-0.7.0-py_0",
        ],
    }


def test_find_supplying_version_null_set_shadows():
    volume = {
        "academic.cli",
        "shadow_academic.cli.AcademicError",
        "academic.cli.clean_bibtex_authors",
    }

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == {"academic": set(), "shadow_academic": {"shadow_academic-0.0.1", "shadow_academic-0.0.2"}}


def test_bad_symbol():
    volume = {"academic.cli.zippy"}

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == set()
    assert bad == volume


def test_bad_symbol_shadows():
    volume = {"shadow_academic.cli.zippy"}

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == set()
    assert bad == volume


def test_symbol_doesnt_exist_recursion_error():
    volume = {"cchardet._cchardet.detect_with_confidence"}

    intersection, bad = find_supplying_version_set(volume, get_symbol_table_func=get_symbol_table_dummy_func)
    assert intersection == set()
    assert bad == volume
