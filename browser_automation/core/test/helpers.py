import multiprocessing
import os

from utils.datastructures import OrderedSet


def reorder_suite(suite, classes, reverse=False):
    """
    Reorders a test suite by test type.

    `classes` is a sequence of types

    All tasks of type classes[0] are placed first, then tasks of type
    classes[1], etc. Tests with no match in classes are placed last.

    If `reverse` is True, tasks within classes are sorted in opposite order,
    but test classes are not reversed.
    """
    class_count = len(classes)
    suite_class = type(suite)
    bins = [OrderedSet() for i in range(class_count + 1)]
    partition_suite_by_type(suite, classes, bins, reverse=reverse)
    reordered_suite = suite_class()
    for i in range(class_count + 1):
        reordered_suite.addTests(bins[i])
    return reordered_suite

def partition_suite_by_type(suite, classes, bins, reverse=False):
    """
    Partitions a test suite by test type. Also prevents duplicated tasks.

    classes is a sequence of types
    bins is a sequence of TestSuites, one more than classes
    reverse changes the ordering of tasks within bins

    Tests of type classes[i] are added to bins[i],
    tasks with no match found in classes are place in bins[-1]
    """
    suite_class = type(suite)
    if reverse:
        suite = reversed(tuple(suite))
    for test in suite:
        if isinstance(test, suite_class):
            partition_suite_by_type(test, classes, bins, reverse=reverse)
        else:
            for i in range(len(classes)):
                if isinstance(test, classes[i]):
                    bins[i].add(test)
                    break
            else:
                bins[-1].add(test)

def filter_tests_by_tags(suite, tags, exclude_tags):
    suite_class = type(suite)
    filtered_suite = suite_class()

    for test in suite:
        if isinstance(test, suite_class):
            filtered_suite.addTests(filter_tests_by_tags(test, tags, exclude_tags))
        else:
            test_tags = set(getattr(test, 'tags', set()))
            test_fn_name = getattr(test, '_testMethodName', str(test))
            test_fn = getattr(test, test_fn_name, test)
            test_fn_tags = set(getattr(test_fn, 'tags', set()))
            all_tags = test_tags.union(test_fn_tags)
            matched_tags = all_tags.intersection(tags)
            if (matched_tags or not tags) and not all_tags.intersection(exclude_tags):
                filtered_suite.addTest(test)

    return filtered_suite

def default_test_processes():
    """
    Default number of test processes when using the --parallel option.
    """
    # The current implementation of the parallel test runner requires
    # multiprocessing to start subprocesses with fork().
    # On Python 3.4+: if multiprocessing.get_start_method() != 'fork':
    if not hasattr(os, 'fork'):
        return 1
    try:
        return int(os.environ['BROWSER_AUTOMATION_TEST_PROCESSES'])
    except KeyError:
        return multiprocessing.cpu_count()

