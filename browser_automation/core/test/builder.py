import os
import unittest
import logging
import sys

from core.test.suites import ParallelTestSuite
from conf import config
from core.test.helpers import \
    (reorder_suite, filter_tests_by_tags, default_test_processes)


logger = logging.getLogger(__name__)

class Builder(object):
    test_suite = unittest.TestSuite
    parallel_test_suite = ParallelTestSuite
    test_runner =  unittest.TextTestRunner
    test_loader = unittest.TestLoader
    #reorder_by = (unittest.TestCase, LiveServerTestCase,)
    reorder_by = ()

    def __init__(self, pattern=None, top_level=None, verbosity=1,
                failfast=False, reverse=False, parallel=0,
                tags=None, exclude_tags=None, test_runner=None, **kwargs):

        self.pattern = pattern or "do_*.py"
        self.top_level = top_level
        self.verbosity = verbosity
        self.failfast = failfast
        self.reverse = reverse
        self.parallel = parallel
        self.tags = set(tags or [])
        self.exclude_tags = set(exclude_tags or [])
        if test_runner:
            self.test_runner = test_runner

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument(
            '-t', '--top-level-directory', action='store', dest='top_level', default=None,
            help='Top level of project for unittest discovery.',
        )
        parser.add_argument(
            '-p', '--pattern', action='store', dest='pattern', default="test*.py",
            help='The test matching pattern. Defaults to do_*.py.',
        )
        parser.add_argument(
            '-r', '--reverse', action='store_true', dest='reverse', default=False,
            help='Reverses test cases order.',
        )
        parser.add_argument(
            '--parallel', dest='parallel', nargs='?', default=1, type=int,
            const=default_test_processes(), metavar='N',
            help='Run tests using up to N parallel processes.',
        )
        parser.add_argument(
            '--tag', action='append', dest='tags',
            help='Run only tests with the specified tag. Can be used multiple times.',
        )
        parser.add_argument(
            '--exclude-tag', action='append', dest='exclude_tags',
            help='Do not run tests with the specified tag. Can be used multiple times.',
        )

    def setup_test_environment(self):
        unittest.installHandler()

    def teardown_test_environment(self, **kwargs):
        unittest.removeHandler()

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        suite = self.test_suite()
        loader = self.test_loader()
        test_labels = test_labels or ['.']
        extra_tests = extra_tests or []

        discover_kwargs = {}
        if self.pattern is not None:
            discover_kwargs['pattern'] = self.pattern
        if self.top_level is not None:
            discover_kwargs['top_level_dir'] = self.top_level

        for label in test_labels:
            tests = None
            kwargs = discover_kwargs.copy()
            relative_path = os.path.join(*label.split('.'))
            label_as_path = os.path.abspath(relative_path)

            # if a module, or "module.ClassName[.method_name]", just run those
            if not os.path.exists(label_as_path):
                tests = loader.loadTestsFromName(label)
            elif os.path.isdir(label_as_path) and not self.top_level:
                tests = loader.discover(start_dir=label_as_path, **kwargs)
            suite.addTests(tests)

        for test in extra_tests:
            suite.addTest(test)

        if self.tags or self.exclude_tags:
            suite = filter_tests_by_tags(suite, self.tags, self.exclude_tags)
        suite = reorder_suite(suite, self.reorder_by, self.reverse)

        if self.parallel > 1:
            parallel_suite = self.parallel_test_suite(suite, self.parallel, self.failfast)

            # Since tasks are distributed across processes on a per-TestCase
            # basis, there's no need for more processes than TestCases.
            parallel_units = len(parallel_suite.subsuites)
            if self.parallel > parallel_units:
                self.parallel = parallel_units

            # If there's only one TestCase, parallelization isn't needed.
            if self.parallel > 1:
                suite = parallel_suite

        return suite

    def run_suite(self, suite, **kwargs):
        result = None
        report_file = os.path.join(config['base_dir'], 'logs', 'html', 'report.html')
        try:
            with open(report_file, 'w') as outfile:
                result = self.test_runner(
                    stream=outfile,
                    verbosity=self.verbosity,
                    failfast=self.failfast,
                ).run(suite)
        except EnvironmentError:
            logger.error("Unexpected error: {0}".format(sys.exc_info()[0]))
        return result

    def suite_result(self, suite, result, **kwargs):
        return suite, result

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        """
        Run the unit tasks for all the test labels in the provided list.

        Test labels should be dotted Python paths to test modules, test
        classes, or test methods.

        A list of 'extra' tasks may also be provided; these tasks
        will be added to the test suite.

        Returns the number of tasks that failed.
        """
        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)
        result = self.run_suite(suite)
        self.teardown_test_environment()
        return self.suite_result(suite, result)


