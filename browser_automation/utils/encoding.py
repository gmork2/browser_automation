import sys
import re
import logging
import os
import datetime
from decimal import Decimal


logger = logging.getLogger(__name__)

_PROTECTED_TYPES = (
    int, type(None), float, Decimal, datetime.datetime, datetime.date, datetime.time
)

def is_protected_type(obj):
    """
    Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_text(strings_only=True).
    """
    return isinstance(obj, _PROTECTED_TYPES)

def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a text object (str) representing s. Treats bytestrings
    using the encoding codec. If strings_only is True, don't convert
    (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if issubclass(type(s), str):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not issubclass(type(s), str):
            if isinstance(s, bytes):
                s = str(s, encoding, errors)
            else:
                s = str(s)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = ' '.join(force_text(arg, encoding, strings_only, errors)
                         for arg in s)
    return s