import warnings
from functools import wraps


try:
    from contextlib import ContextDecorator
except ImportError:
    ContextDecorator = None


class classonlymethod(classmethod):
    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError("This method is available only on the class, not on instances.")
        return super(classonlymethod, self).__get__(instance, cls)


class classproperty(object):
    def __init__(self, method=None):
        self.method = method

    def __get__(self, instance, cls=None):
        return self.method(cls)

    def getter(self, method):
        self.method = method
        return self


def deprecated(func):
    """
    This is a decorator which can be used to mark function as deprecated.
    It will result in a warning being emmitted when the function is used.
    """

    @wraps(func)
    def depr_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # Turn off filter
        warnings.warn('Call to deprecated function {}.'.format(func.__name__),
                      category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # Reset filter
        return func(*args, **kwargs)

    return depr_func

def tag(*tags):
    """
    Decorator to add tags to a test class or method.
    """
    def decorator(obj):
        setattr(obj, 'tags', set(tags))
        return obj
    return decorator

