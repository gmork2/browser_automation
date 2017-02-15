from conf import settings
from utils.loading import import_string
from utils.version import get_version
from conf import VERSION

__version__ = get_version(VERSION)

# First find the logging configuration function, then
# invoke it with the logging conf
if settings.LOGGING_CONFIG:
    try:
        logging_config_func = import_string(settings.LOGGING_CONFIG)
    except ImportError:
        raise
    if settings.LOGGING:
        logging_config_func(settings.LOGGING)
