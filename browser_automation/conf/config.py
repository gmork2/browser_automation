import logging
import os
from collections import ChainMap

from conf.helpers import get_default_config_dir


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

        # Load the config from file in the config_dir
        self.__config_file = os.path.join(config_dir, 'conf', filename) \
                if config_dir else get_default_config_dir(filename)

    def __contains__(self, item):
        return item in self.__config

    def __bool__(self):
        return bool(self.__config)

    def __setitem__(self, key, value):
        """
        Sets item 'key' to 'value' in the config dictionary.
        Does not allow changing the item's type unless it is None.
        If the types do not match it will raise a ValueError.
        """
        # Do not allow the value type to change unless it is None
        if key in self.__config \
            and value is not None \
            and not isinstance(self.__config[key], type(None)) \
            and not isinstance(self.__config[key], type(value)):
            logger.error('Value Type "{0}" invalid for key: {1}|{2}'
                           .format(type(value), key, type(self.__config[key])))
            raise ValueError
        # Convert any key object to lower string
        else:
            self.__config[str(key).lower()] = value
            logger.debug('Setting key "{0}" to: {1} (of type: {2})'
                         .format(key, value, type(value)))

    def __getitem__(self, key):
        """
        Get item with a specific key from the configuration. Lookups search the
        underlying mappings successively until a key is found.
        """
        try:
            return self.__config[key]
        except KeyError:
            pass
        return self.__missing__(key)

    def __missing__(self, key):
        raise KeyError(key)

    def __delitem__(self, key):
        """
        Delete item with a specific key from the configuration. Deletions only
        operate on the first mapping.
        """
        del self.__config[key]

    def __del__(self):
        pass

    def get(self, key, default):
        return self[key] if key in self else default

    def new_child(self, m=None):
        return self.__config.new_child(m)

    @property
    def parents(self):
        return self.__config.parents

    def popitem(self):
        return self.__config.popitem()

    def pop(self, key, args):
        return self.__config.pop(key, args)

    def clear(self):
        self.__config.clear()