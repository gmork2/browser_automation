from argparse import ArgumentParser
import unittest
import pytest

from core.test.builder import Builder


class TestBuilder:

    def test_init_parallel(self):
        runner = Builder()
        assert runner.parallel == 0

    def test_add_arguments_parallel(self):
        parser = ArgumentParser()
        Builder.add_arguments(parser)

        ns = parser.parse_args([])
        assert ns.parallel == 1
        ns = parser.parse_args(["--parallel", "4"])
        assert ns.parallel == 4

    def test_dotted_test_module(self):
        count = Builder(pattern='*.py').build_suite(
            ['misc.tests.test_discovery_sample'],
        ).countTestCases()

        assert count == 3

    def test_dotted_test_class_more_tests(self):
        count = Builder().build_suite(
            ['misc.tests.test_discovery_sample.more_tests.do_sample.Test'],
        ).countTestCases()

        assert count == 1

    def test_dotted_test_class_vanilla_unittest(self):
        count = Builder().build_suite(
            ['misc.tests.test_discovery_sample.do_sample.TestVanillaUnittest'],
        ).countTestCases()

        assert count == 1

    def test_dotted_test_method_testcase(self):
        count = Builder().build_suite(
            ['misc.tests.test_discovery_sample.do_sample.TestSimpleTestCase.test_sample'],
        ).countTestCases()

        assert count == 1

    def test_pattern(self):
        count = Builder(
            pattern="*.py",
        ).build_suite(['misc.tests.test_discovery_sample']).countTestCases()

        assert count == 3

    def test_empty_test_case(self):
        count = Builder().build_suite(
            ['misc.tests.test_discovery_sample.do_sample.EmptyTestCase'],
        ).countTestCases()

        assert count == 0

    def test_discovery_on_package(self):
        count = Builder().build_suite(
            ['misc.tests.test_discovery_sample.more_tests'],
        ).countTestCases()

        assert count == 1

    @pytest.mark.skip(reason="Pending revision")
    def test_testcase_ordering(self):
        suite = Builder().build_suite(['misc.tests.test_discovery_sample.do_sample'])
        assert suite._tests[0].__class__.__name__ == 'TaggedTestCase', \
            "TaggedTestCase should be the first test case"
        assert suite._tests[2].__class__.__name__ == 'TestSimpleTestCase', \
            "TestSimpleTestCase should be the first test case"

        # All others can follow in unspecified order, including doctests
        assert 'DocTestCase' in [t.__class__.__name__ for t in suite._tests[2:]]

    @pytest.mark.skip(reason="Pending revision")
    def test_reverse(self):
        # Reverse should reorder tests while maintaining the grouping specified
        # by ``Builder.reorder_by``.
        runner = Builder(reverse=True)
        suite = runner.build_suite(test_labels=(['misc.tests.test_discovery_sample.do_sample']))

        suite = tuple(suite)
        assert 'doctests' in suite[0].id(), "Test groups should not be reversed."
        assert 'TaggedTestCase' in suite[4].id(), "Test groups order should be preserved."
        assert 'factorial' in suite[0].id(), "Test cases should be reversed."
        assert 'test_single_tag' in suite[3].id(), "Test groups order should be preserved."
        assert 'test_multiple_tags' in suite[4].id(), "Test groups order should be preserved."

    def test_overridable_test_suite(self):
        assert Builder().test_suite == unittest.TestSuite

    def test_overridable_test_runner(self):
        assert Builder().test_runner == unittest.TextTestRunner

    def test_overridable_test_loader(self):
        assert Builder().test_loader == unittest.TestLoader

    def test_tags(self):
        runner = Builder(tags=['core'])
        assert runner.build_suite(['misc.tests.test_discovery_sample.do_sample']).countTestCases() == 1
        runner = Builder(tags=['fast'])
        assert runner.build_suite(['misc.tests.test_discovery_sample.do_sample']).countTestCases() == 2
        runner = Builder(tags=['slow'])
        assert runner.build_suite(['misc.tests.test_discovery_sample.do_sample']).countTestCases() == 2
        runner = Builder(tags=['tiny'])
        assert runner.build_suite(['misc.tests.test_discovery_sample.do_sample']).countTestCases() == 0

    @pytest.mark.skip(reason="Pending revision")
    def test_exclude_tags(self):
        runner = Builder(tags=['fast'], exclude_tags=['core'])
        assert runner.build_suite(['misc.tests.test_discovery_sample.do_sample']).countTestCases() == 1
        runner = Builder(tags=['fast'], exclude_tags=['slow'])
        assert runner.build_suite(['misc.tests.test_discovery_sample.do_sample']).countTestCases() == 0
        runner = Builder(exclude_tags=['slow'])
        assert runner.build_suite(['misc.tests.test_discovery_sample.do_sample']).countTestCases() == 3


