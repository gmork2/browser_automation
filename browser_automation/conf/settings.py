# -*- coding: utf-8 -*-
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# When True, turns on debug mode.
DEBUG = True

# Local time zone for this installation. All choices can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
# systems may support all possibilities). When USE_TZ is True, this is
# interpreted as the default user time zone.
TIME_ZONE = 'America/Chicago'

# If you set this to True, will use timezone-aware datetimes.
USE_TZ = False

# Default content type and charset to use for all email messages, if a
# MIME type isn't manually specified. These are used to construct the
# Content-Type header.
DEFAULT_CONTENT_TYPE = 'text/html'
DEFAULT_CHARSET = 'utf-8'

# Encoding of files read from disk.
FILE_CHARSET = 'utf-8'

# Email address that error messages come from.
SERVER_EMAIL = 'root@localhost'

# The email backend to use. The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND = 'browser_automation.core.mail.smtp.EmailBackend'

# Host for sending email.
EMAIL_HOST = 'localhost'

# Port for sending email.
EMAIL_PORT = 25

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None

# Templates folders
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Use {HOST}, {PORT} or {FILE}
SERVICE_OPTIONS = "--port={PORT}"
SERVICE_EXECUTABLE = os.path.join(BASE_DIR, 'bin', 'drivers', 'chromedriver.exe')

# Host for webdriver service
SERVICE_HOST = 'localhost'

# The specified ports to listen on. It may be of the form
# '8000-8010,8080,9200-9300'
SERVICE_PORT = '4444-4454'

# The callable to use to configure logging
LOGGING_CONFIG = 'logging.config.dictConfig'

# Default logging. If you don’t want to configure logging at all
# (or you want to manually configure logging using your own approach),
# set LOGGING_CONFIG to None and provide a new configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'browser_automation.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'browser_automation.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
        },
    },
    'loggers': {
        'browser_automation': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'INFO',
        },
    }
}


