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


class TestProgram(unittest.TestProgram):
    """
    A variation of the unittest.TestProgram. Please refer to the base
    class for command line parameters. In the future we may
    build our own launcher to support more specific command line
    parameters.
    """
    def runTests(self):
        # Pick HTMLTestRunner as the default test runner.
        # base class's testRunner parameter is not useful because it means
        # we have to instantiate HTMLTestRunner before we know self.verbosity.
        if self.testRunner is None:
            self.testRunner = HTMLTestRunner(verbosity=self.verbosity)
        super().runTests()

# Facilities for running tasks from the command line
main = TestProgram

