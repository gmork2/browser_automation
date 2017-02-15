import os
from importlib import import_module

from conf import settings as global_settings
from utils.lazy import LazyObject, empty
from core.exceptions import ImproperlyConfigured
from conf.config import Config


ENVIRONMENT_VARIABLE = "BROWSER_AUTOMATION_SETTINGS"

class LazyConfig(LazyObject):
    """
    A lazy proxy for either global settings or a custom settings
    object. The user can manually configure settings prior to using
    them. Otherwise, Browser automation uses the settings module
    pointed to by BROWSER_AUTOMATION_SETTINGS.
    """
    def _setup(self, name=None):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has not
        previously configured the settings manually.
        """
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            desc = ("setting %s" % name) if name else "settings"
            raise ImproperlyConfigured(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, ENVIRONMENT_VARIABLE))
        try:
            settings = import_module(settings_module)
        except ImportError:
            raise ImproperlyConfigured("Couldn't import %s" % settings_module)

        self._wrapped = Config(defaults=vars(settings))

    def __repr__(self):
        # Hardcode the class name as otherwise it yields 'Settings'.
        if self._wrapped is empty:
            return '<LazySettings [Unevaluated]>'
        return '<LazySettings "%(settings_module)s">' % {
            'settings_module': self._wrapped.__repr__(),
        }

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup(name)
        return self._wrapped[name]

    __getitem__ = __getattr__

    def __setitem__(self, name, value):
        if name == "_wrapped":
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is empty:
                self._setup()
            self._wrapped[name] = value

    def get(self, key, default):
        try:
            return self[key]
        except KeyError:
            return default

    def configure(self, config_cls=Config, default_settings=global_settings, **options):
        """
        Called to manually configure the settings. The 'default_settings'
        parameter sets where to retrieve any unspecified values from (its
        argument must support attribute access (__getattr__)).
        """
        if self._wrapped is not empty:
            raise RuntimeError('Settings already configured.')
        holder = config_cls(options)


        for setting in dir(default_settings):
            if setting.isupper():
                holder[setting.lower()] = getattr(default_settings, setting)

        self._wrapped = holder

    @property
    def configured(self):
        """
        Returns True if the settings have already been configured.
        """
        return self._wrapped is not empty
