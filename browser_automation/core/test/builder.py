import unittest
import logging

from core.test.suites import ParallelTestSuite


logger = logging.getLogger(__name__)


class Builder(object):
    test_suite = unittest.TestSuite
    parallel_test_suite = ParallelTestSuite
    test_runner =  unittest.TextTestRunner
    test_loader = unittest.TestLoader
    reorder_by = ()
    
