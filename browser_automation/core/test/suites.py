import ctypes
import logging
import multiprocessing
import unittest
import itertools

try:
    import tblib.pickling_support
except ImportError:
    tblib = None

logger = logging.getLogger(__name__)


def partition_suite_by_case(suite):
    """
    Partitions a test suite by test case, preserving the order of tasks.
    """
    groups = []
    suite_class = type(suite)
    for test_type, test_group in itertools.groupby(suite, type):
        if issubclass(test_type, unittest.TestCase):
            groups.append(suite_class(test_group))
        else:
            for item in test_group:
                groups.extend(partition_suite_by_case(item))
    return groups

class ParallelTestSuite(unittest.TestSuite):
    """
    Run a series of tests in parallel in several processes.

    While the unittest module's documentation implies that orchestrating the
    execution of tasks is the responsibility of the test runner, in practice,
    it appears that TestRunner classes are more concerned with formatting and
    displaying test results.

    Since there are fewer use cases for customizing TestSuite than TestRunner,
    implementing parallelization at the level of the TestSuite improves
    interoperability with existing custom test runners. A single instance of a
    test runner can still collect results from all tasks without being aware
    that they have been run in parallel.
    """

    def __init__(self, suite, processes, failfast=False):
        self.subsuites = partition_suite_by_case(suite)
        self.processes = processes
        self.failfast = failfast
        super(ParallelTestSuite, self).__init__()

    def run(self, result):
        """
        Distribute test cases across workers.

        Return an identifier of each test case with its result in order to use
        imap_unordered to show results as soon as they're available.

        To minimize pickling errors when getting results from workers:

        - pass back numeric indexes in self.subsuites instead of tasks
        - make tracebacks picklable with tblib, if available

        Even with tblib, errors may still occur for dynamically created
        exception classes which cannot be unpickled.
        """
        if tblib is not None:
            tblib.pickling_support.install()

        counter = multiprocessing.Value(ctypes.c_int, 0)
        pool = multiprocessing.Pool(
            processes=self.processes,
            initializer=self.init_worker.__func__,
            initargs=[counter])
        args = [
            (index, subsuite, self.failfast)
            for index, subsuite in enumerate(self.subsuites)
        ]
        test_results = pool.imap_unordered(self.run_subsuite.__func__, args)

        while True:
            if result.shouldStop:
                pool.terminate()
                break

            try:
                subsuite_index, events = test_results.next(timeout=0.1)
            except multiprocessing.TimeoutError:
                continue
            except StopIteration:
                pool.close()
                break

            tests = list(self.subsuites[subsuite_index])
            for event in events:
                event_name = event[0]
                handler = getattr(result, event_name, None)
                if handler is None:
                    continue
                test = tests[event[1]]
                args = event[2:]
                handler(test, *args)

        pool.join()

        return result
