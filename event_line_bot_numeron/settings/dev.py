import os

from .base import *  # noqa: F401,F403
from .utils import strtobool

DEBUG = strtobool(os.environ.get("DEBUG", "y"))

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
