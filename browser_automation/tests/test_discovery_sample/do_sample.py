import doctest
from unittest import TestCase

from utils.decorators import tag
from . import doctests


class TestVanillaUnittest(TestCase):

    def test_sample(self):
        self.assertEqual(1, 1)


class EmptyTestCase(TestCase):
    pass


@tag('slow')
class TaggedTestCase(TestCase):

    @tag('fast')
    def test_single_tag(self):
        self.assertEqual(1, 1)

    @tag('fast', 'core')
    def test_multiple_tags(self):
        self.assertEqual(1, 1)


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(doctests))
    return tests
