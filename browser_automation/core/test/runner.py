import unittest
import datetime
import sys


class HTMLTestRunner(object):
    def __init__(self, stream=sys.stdout, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None, warnings=None,
                 *, tb_locals=False, **kwargs):
        self.verbosity = verbosity
        self.title = None
        self.description = None
        self.startTime = datetime.datetime.now()
        self.stream = stream



