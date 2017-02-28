import unittest
import functools
import time

from conf import config


class CheckCondition(object):
    """
    Descriptor class for deferred condition checking
    """
    def __init__(self, cond_func):
        self.cond_func = cond_func

    def __get__(self, instance, cls=None):
        return self.cond_func()


def skipUnlessHasAttr(attrs):
    """
    Decorater function to skip test unless has attribute.
    """
    def decorator(test_func):
        @functools.wraps(test_func)
        def skip_wrapper(self, *args):
            if all([hasattr(self, attr) for attr in attrs]):
                test_func(self, *args)
            else:
                attr_list = ', '.join([attr for attr in attrs if not hasattr(self, attr)])
                unittest.skip("{!r} doesn't have {!r}".format(self, attr_list))
        return skip_wrapper
    return decorator


def skipIfRobotsDeny(url):
    raise NotImplemented


def _deferredSkip(condition, reason):
    def decorator(test_func):
        if not (isinstance(test_func, type) and
                issubclass(test_func, unittest.TestCase)):
            @functools.wraps(test_func)
            def skip_wrapper(*args, **kwargs):
                if condition():
                    raise unittest.SkipTest(reason)
                return test_func(*args, **kwargs)
            test_item = skip_wrapper
        else:
            # Assume a class is decorated
            test_item = test_func
            test_item.__unittest_skip__ = CheckCondition(condition)
        test_item.__unittest_skip_why__ = reason
        return test_item
    return decorator


def skipUnlessConfigAttribute(*attributes):
    """
    Skip a task if config has at least one of the named attributes.
    """
    return _deferredSkip(
        lambda: not all(config.get(attribute, False) for attribute in attributes),
        "Config has attribute(s) %s" % ", ".join(attributes)
    )

requires_tz_support = unittest.skipUnless(
    hasattr(time, 'tzset'),
    "This test relies on the ability to run a program in an arbitrary "
    "time zone, but your operating system isn't able to do that."
)

class TestContextDecorator(object):
    """
    A base class that can either be used as a context manager during tests
    or as a test function or unittest.TestCase subclass decorator to perform
    temporary alterations.

    `attr_name`: attribute assigned the return value of enable() if used as
                 a class decorator.

    `kwarg_name`: keyword argument passing the return value of enable() if
                  used as a function decorator.
    """
    def __init__(self, attr_name=None, kwarg_name=None):
        self.attr_name = attr_name
        self.kwarg_name = kwarg_name

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def __enter__(self):
        return self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def decorate_class(self, cls):
        if issubclass(cls, unittest.TestCase):
            decorated_setUp = cls.setUp
            decorated_tearDown = cls.tearDown

            def setUp(inner_self):
                context = self.enable()
                if self.attr_name:
                    setattr(inner_self, self.attr_name, context)
                decorated_setUp(inner_self)

            def tearDown(inner_self):
                decorated_tearDown(inner_self)
                self.disable()

            cls.setUp = setUp
            cls.tearDown = tearDown
            return cls
        raise TypeError('Can only decorate subclasses of unittest.TestCase')

    def decorate_callable(self, func):
        @functools.wraps(func, assigned=functools.WRAPPER_ASSIGNMENTS)
        def inner(*args, **kwargs):
            with self as context:
                if self.kwarg_name:
                    kwargs[self.kwarg_name] = context
                return func(*args, **kwargs)
        return inner

    def __call__(self, decorated):
        if isinstance(decorated, type):
            return self.decorate_class(decorated)
        elif callable(decorated):
            return self.decorate_callable(decorated)
        raise TypeError('Cannot decorate object of type %s' % type(decorated))








