import logging

from conf import config


class RequireDebugFalse(logging.Filter):
    def filter(self, record):
        return not config['debug']


class RequireDebugTrue(logging.Filter):
    def filter(self, record):
        return config['debug']