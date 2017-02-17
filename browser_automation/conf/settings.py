# -*- coding: utf-8 -*-
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The email backend to use. The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND = 'browser_automation.core.mail.smtp.EmailBackend'

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
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
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


