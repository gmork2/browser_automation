"""
Exceptions that may happen in all the webdriver code.
"""


class WebDriverException(Exception):
    """
    Base webdriver exception.
    """
    pass


class NoSuchElement(WebDriverException):
    """
    Thrown when element could not be found.
    """
    pass


class NoSuchFrame(WebDriverException):
    """
    Thrown when frame target to be switched doesn't exist.
    """
    pass


class UnknownCommand(WebDriverException):
    """
    Thrown when server cant recognize a command.
    """
    pass


class StaleElementReference(WebDriverException):
    """
    Thrown when a reference to an element is now "stale".
    Stale means the element no longer appears on the DOM of the page.
    """
    pass


class ElementNotVisible(WebDriverException):
    """
    Thrown when an element is present on the DOM, but
    it is not visible, and so is not able to be interacted with.
    """
    pass


class InvalidElementState(WebDriverException):
    """

    """
    pass


class JavaScriptError(WebDriverException):
    """

    """
    pass


class XPathLookupError(WebDriverException):
    """

    """
    pass


class Timeout(WebDriverException):
    """
    Thrown when a command does not complete in enough time.
    """
    pass


class NoSuchWindow(WebDriverException):
    """
    Thrown when window target to be switched doesn't exist.
    """
    pass


class InvalidCookieDomain(WebDriverException):
    """
    Thrown when attempting to add a cookie under a different domain
    than the current URL.
    """
    pass


class ScriptTimeout(WebDriverException):
    """

    """
    pass


class InvalidSelector(WebDriverException):
    """
    Thrown when the selector which is used to find an element does not return
    a WebElement.
    """
    pass


class SessionNotCreatedException(WebDriverException):
    """

    """
    pass


class NoSuchSession(WebDriverException):
    """

    """
    pass


class UnexpectedAlertOpen(WebDriverException):
    """
    Thrown when an unexpected alert is appeared.
    """
    pass


class NoAlertOpen(WebDriverException):
    """
    Thrown when switching to no presented alert.
    """
    pass


class UnknownError(WebDriverException):
    """
    Thrown when error is unknown.
    """
    pass


def exception_for_legacy_response(response):
    exception_class_map = {
        6: NoSuchSession,
        7: NoSuchElement,
        8: NoSuchFrame,
        9: UnknownCommand,
        10: StaleElementReference,
        11: ElementNotVisible,
        12: InvalidElementState,
        13: UnknownError,
        17: JavaScriptError,
        19: XPathLookupError,
        21: Timeout,
        23: NoSuchWindow,
        24: InvalidCookieDomain,
        26: UnexpectedAlertOpen,
        27: NoAlertOpen,
        28: ScriptTimeout,
        32: InvalidSelector,
        33: SessionNotCreatedException
    }

    return exception_class_map \
        .get(response['status'],
             WebDriverException)(response['value']['message'])

def exception_for_standard_response(response):
    exception_map = {
        'no such session' : NoSuchSession,
        'no such element': NoSuchElement,
        'no such frame': NoSuchFrame,
        'unknown command': UnknownCommand,
        'stale element reference': StaleElementReference,
        'element not visible': ElementNotVisible,
        'invalid element state': InvalidElementState,
        'unknown error': UnknownError,
        'javascript error': JavaScriptError,
        'xpath lookup error': XPathLookupError,
        'timeout': Timeout,
        'no such window': NoSuchWindow,
        'invalid cookie domain': InvalidCookieDomain,
        'unexpected alert open': UnexpectedAlertOpen,
        'no alert open': NoAlertOpen,
        'asynchronous script timeout': ScriptTimeout,
        'invalid selector': InvalidSelector,
        'session not created exception': SessionNotCreatedException
    }
    return exception_map \
        .get(response['error'],
             WebDriverException)(response['message'])