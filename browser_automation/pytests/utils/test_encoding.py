# -*- encoding: utf-8 -*-
import datetime
import pytest

from utils.lazy import LazyObject
from utils.encoding import force_bytes, force_text


class TestEncodingUtils:
    def test_force_text_exception(self):
        """
        Broken __unicode__/__str__ actually raises an error.
        """
        class Foo(object):
            def __str__(self):
                return b'\xc3\xb6\xc3\xa4\xc3\xbc'
            __unicode__ = __str__

        # str(s) raises a TypeError if the result is not a text type.
        exception = TypeError
        with pytest.raises(exception):
            force_text(Foo())

    def test_force_text_lazy(self):
        class AdHocLazyObject(LazyObject):
            def __init__(self, func):
                self.__dict__['_setupfunc'] = func
                super(AdHocLazyObject, self).__init__()

            def _setup(self):
                self._wrapped = self._setupfunc()

        s = AdHocLazyObject(lambda: 'x')
        assert issubclass(type(force_text(s)), str)

    def test_force_bytes_exception(self):
        """
        force_bytes knows how to convert to bytes an exception
        containing non-ASCII characters in its args.
        """
        error_msg = "This is an exception, voilà"
        exc = ValueError(error_msg)
        result = force_bytes(exc)
        assert result == error_msg.encode('utf-8')

    def test_force_bytes_strings_only(self):
        today = datetime.date.today()
        force_bytes(today, strings_only=True) == today

