from . import version
from .version import get_versions
from . import core
from .core import *
from requests import *


def xyz():
    return get_versions()
