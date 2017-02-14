import logging
import os
from collections import ChainMap


logger = logging.getLogger(__name__)

class Config(object):
    def __new__(cls, filename=None, defaults=None, config_dir=None, file_version=1):
        # Implements a singleton pattern
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        if not isinstance(cls.instance, cls):
            raise AttributeError(
                "Error trying to return a valid class instance")
        return cls.instance

    def __init__(self, filename=None, defaults={}, config_dir=None, file_version=1):
        self.__config = ChainMap({
            key.lower():value for key, value in defaults.items()
            if isinstance(key, str) and key.isupper()
        })

        self.__config_disabled = list()
        self.__set_functions = dict()
        self.__change_callbacks = list()

        # These hold the version numbers and they will be set when loaded
        self.__version = {
            'format': 1,
            'file': file_version
        }
