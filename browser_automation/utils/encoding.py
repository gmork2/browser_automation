import sys
import re
import logging
import os
import datetime
from decimal import Decimal


logger = logging.getLogger(__name__)

WHITESPACE = re.compile('\s+')

_PROTECTED_TYPES = (
    int, type(None), float, Decimal, datetime.datetime, datetime.date, datetime.time
)

class Promise(object):
    """
    This is just a base class for the proxy class created in
    the closure of the lazy function. It can be used to recognize
    promises in code.
    """
    pass

def normalize_whitespace(string):
    return WHITESPACE.sub(' ', string)

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

def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to force_text, except that lazy instances are resolved to
    bytestrings.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if strings_only and is_protected_type(s):
        return s
    if isinstance(s, memoryview):
        return bytes(s)
    if isinstance(s, Promise):
        return str(s).encode(encoding, errors)
    if not isinstance(s, str):
        try:

            return str(s).encode(encoding)

        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return b' '.join(force_bytes(arg, encoding, strings_only, errors)
                                 for arg in s)
            return str(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)

