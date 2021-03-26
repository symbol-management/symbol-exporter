import argparse
import re
import importlib
from pprint import pprint

from . import CompiledPythonLib
from .utils import logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--compare")
    args = parser.parse_args()
    results = CompiledPythonLib(args.filename).find_symbols()

    if args.print:
        pprint(results)

    if args.compare:
        module = importlib.import_module(args.compare)
        pattern = re.compile(r"__.+__")
        expected = {s for s in dir(module) if not pattern.fullmatch(s)}
        actual = {x["name"] for x in results["methods"] if not pattern.fullmatch(x["name"])}
        actual |= {x["name"] for x in results["objects"] if not pattern.fullmatch(x["name"])}
        if actual - expected:
            raise NotImplementedError("Found unexpected keys", actual - expected)
        if expected - actual:
            logger.warning("Failed to find some keys: %s", expected - actual)
        else:
            logger.info("Found all symbols successfully")


if __name__ == "__main__":
    parse_args()
