import _pickle as pickle
import json
import logging
import os
import shutil
from collections import ChainMap

from utils.json import find_json_objects
from conf.helpers import get_default_config_dir


logger = logging.getLogger(__name__)

class Config(object):
    """
    This class is used to access/create/modify config files. The format of the config
    file is two json encoded dicts: <version dict> <content dict>
    The version dict contains two keys: file and format.  The format version is
    controlled by the Config class. It should only be changed when anything below
    it is changed directly by the Config class.  An example of this would be if we
    changed the serializer for the content to something different.
    The config file version is changed by the 'owner' of the config file.  This is
    to signify that there is a change in the naming of some config keys or something
    similar along those lines.
    The content is simply the dict to be saved and will be serialized before being
    written.
    Since the format of the config could change, there needs to be a way to have
    the Config object convert to newer formats.  To do this, you will need to
    register conversion functions for various versions of the config file. Note that
    this can only be done for the 'config file version' and not for the 'format'
    version as this will be done internally.
    """
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

    def register_change_callback(self, callback):
        """
        Register a callback function for any changed value. Will be
        called when any value is changed in the config dictionary.
        """
        self.__change_callbacks.append(callback)

    def register_set_function(self, key, function, apply_now=True):
        """
        Register a function to be called when a config value changes.
        """
        logger.debug('Registering function for %s key..', key)
        if key not in self.__set_functions:
            self.__set_functions[key] = []

        self.__set_functions[key].append(function)

        # Run the function now if apply_now is set
        if apply_now:
            function(key, self.__config[key])
        return

    def apply_all(self):
        """
        Calls all set functions.
        """
        logger.debug('Calling all set functions..')
        for key, value in self.__set_functions.items():
            for func in value:
                func(key, self.__config[key])

    def apply_set_functions(self, key):
        logger.debug('Calling set functions for key %s..', key)
        if key in self.__set_functions:
            for func in self.__set_functions[key]:
                func(key, self.__config[key])

    def load(self, filename=None):
        """
        Load a config file.
        """
        if not filename:
            filename = self.__config_file

        try:
            with open(filename, 'r') as _file:
                data = _file.read()
        except IOError as ex:
            logger.warning('Unable to open config file %s: %s', filename, ex)
            return

        objects = find_json_objects(data)

        if not len(objects):
            # No json objects found, try depickling it
            try:
                self.__config.update(pickle.loads(data))
            except Exception as ex:
                logger.exception(ex)
                logger.warning('Unable to load config file: %s', filename)
        elif len(objects) == 1:
            start, end = objects[0]
            try:
                self.__config.update(json.loads(data[start:end]))
            except Exception as ex:
                logger.exception(ex)
                logger.warning('Unable to load config file: %s', filename)
        elif len(objects) == 2:
            try:
                start, end = objects[0]
                self.__version.update(json.loads(data[start:end]))
                start, end = objects[1]
                self.__config.update(json.loads(data[start:end]))
            except Exception as ex:
                logger.exception(ex)
                logger.warning('Unable to load config file: %s', filename)

        logger.debug('Config %s version: %s.%s loaded: %s', filename,
                     self.__version['format'], self.__version['file'], self.__config)

    def save(self, filename=None):
        """
        Save configuration to disk.
        """
        if not filename:
            filename = self.__config_file
        # Check to see if the current config differs from the one on disk
        # We will only write a new config file if there is a difference
        try:
            with open(filename, 'r') as _file:
                data = _file.read()
            objects = find_json_objects(data)
            start, end = objects[0]
            version = json.loads(data[start:end])
            start, end = objects[1]
            loaded_data = json.loads(data[start:end])
            if self.__config == loaded_data and self.__version == version:
                # The config has not changed so lets just return
                return True
        except (IOError, IndexError) as ex:
            logger.warning('Unable to open config file: %s because: %s', filename, ex)

        # Save the new config and make sure it's written to disk
        try:
            logger.debug('Saving new config file %s', filename + '.new')
            with open(filename + '.new', 'w') as _file:
                json.dump(self.__version, _file, indent=2)
                json.dump(self.__config, _file, indent=2, sort_keys=True)
                _file.flush()
                os.fsync(_file.fileno())
        except IOError as ex:
            logger.error('Error writing new config file: %s', ex)
            return False

        # Make a backup of the old config
        try:
            logger.debug('Backing up old config file to %s.bak', filename)
            shutil.move(filename, filename + '.bak')
        except IOError as ex:
            logger.warning('Unable to backup old config: %s', ex)

        # The new config file has been written successfully, so let's move it over
        # the existing one.
        try:
            logger.debug('Moving new config file %s to %s..', filename + '.new', filename)
            shutil.move(filename + '.new', filename)
        except IOError as ex:
            logger.error('Error moving new config file: %s', ex)
            return False
        else:
            return True

    def run_converter(self, input_range, output_version, func):
        """
        Runs a function that will convert file versions.
        """
        if output_version in input_range or output_version <= max(input_range):
            raise ValueError('output_version needs to be greater than input_range')

        if self.__version['file'] not in input_range:
            logger.debug('File version %s is not in input_range %s, ignoring converter function..',
                         self.__version['file'], input_range)
            return

        try:
            self.__config = func(self.__config)
        except Exception as ex:
            logger.exception(ex)
            logger.error('There was an exception try to convert config file %s %s to %s',
                         self.__config_file, self.__version['file'], output_version)
            raise ex
        else:
            self.__version['file'] = output_version
            self.save()

    @property
    def config_file(self):
        return self.__config_file

    def __repr__(self):
        import pprint
        return str(pprint.pformat(self.__config))

