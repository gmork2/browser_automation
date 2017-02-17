"""SMTP email backend class."""
import smtplib
import ssl
import threading
from email.header import Header
from email.utils import getaddresses, parseaddr

from utils.encoding import force_text


class EmailBackend(object):
    """
    A wrapper that manages the SMTP network connection.
    """
    pass