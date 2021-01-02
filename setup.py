from setuptools import setup, find_packages

setup(
    name="symbol-exporter",
    version="0.0.1",
    author="CJ-Wright",
    url="https://github.com/symbol-management/symbol-exporter",
    include_package_data=True,
    packages=find_packages(exclude=["tests"]),
    package_dir={"symbol_exporter": "symbol_exporter"},
)
