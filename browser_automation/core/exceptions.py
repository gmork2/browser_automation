"""
Global app exception and warning classes.
"""

class HTMLParseError(Exception):
    """

    """
    pass


class FieldDoesNotExist(Exception):
    """
    The field does not exist
    """
    pass


class ObjectDoesNotExist(Exception):
    """
    The current object does not exist
    """
    silent_variable_failure = True


class MultipleObjectsReturned(Exception):
    """
    The query returned multiple objects when only one was expected
    """
    pass


class SuspiciousOperation(Exception):
    """
    The web did something suspicious
    """


class SuspiciousMultipartForm(SuspiciousOperation):
    """
    Suspect MIME request in multipart form data
    """
    pass


class SuspiciousFileOperation(SuspiciousOperation):
    """
    A Suspicious filesystem operation was attempted
    """
    pass


class DisallowedHost(SuspiciousOperation):
    """
    HTTP_HOST header contains invalid value
    """
    pass


class DisallowedRedirect(SuspiciousOperation):
    """
    Redirect to scheme not in allowed list
    """
    pass


class TooManyFieldsSent(SuspiciousOperation):
    """
    The number of fields in a GET or POST request exceeded
    conf.DATA_UPLOAD_MAX_NUMBER_FIELDS.
    """
    pass


class ResponseDataTooBig(SuspiciousOperation):
    """
    The size of the response (excluding any file downloads) exceeded
    conf.DATA_UPLOAD_MAX_MEMORY_SIZE.
    """
    pass


class PermissionDenied(Exception):
    """
    We did not have permission to do that
    """
    pass


class ResponseDoesNotExist(Exception):
    """
    The response does not exist
    """
    pass


class ImproperlyConfigured(Exception):
    """
    Somehow improperly configured
    """
    pass


class FieldError(Exception):
    """
    Some kind of problem with a field
    """
    pass