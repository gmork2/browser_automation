from utils.loading import import_string
from conf import config


def get_connection(backend=None, fail_silently=False, **kwds):
    """
    Load an email backend and return an instance of it.

    If backend is None (default) config['email_backend'] is used.

    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    cls = import_string(backend or config['email_backend'])
    return cls(fail_silently=fail_silently, **kwds)