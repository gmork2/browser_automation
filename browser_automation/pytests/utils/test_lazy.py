import copy
import pickle
import pytest

from utils.lazy import LazyObject, empty


class Foo(object):
    """
    A simple class with just one attribute.
    """
    foo = 'bar'

    def __eq__(self, other):
        return self.foo == other.foo


class TestLazyObject:
    def lazy_wrap(self, wrapped_object):
        """
        Wrap the given object into a LazyObject
        """
        class AdHocLazyObject(LazyObject):
            def _setup(self):
                self._wrapped = wrapped_object

        return AdHocLazyObject()

    def test_getattr(self):
        obj = self.lazy_wrap(Foo())
        assert obj.foo == 'bar'

    def test_setattr(self):
        obj = self.lazy_wrap(Foo())
        obj.foo = 'BAR'
        obj.bar = 'baz'
        assert obj.foo == 'BAR'
        assert obj.bar == 'baz'

    def test_setattr2(self):
        # Same as test_setattr but in reversed order
        obj = self.lazy_wrap(Foo())
        obj.bar = 'baz'
        obj.foo = 'BAR'
        assert obj.foo == 'BAR'
        assert obj.bar == 'baz'

    def test_delattr(self):
        obj = self.lazy_wrap(Foo())
        obj.bar = 'baz'
        assert obj.bar == 'baz'
        del obj.bar
        with pytest.raises(AttributeError):
            obj.bar

    def test_cmp(self):
        obj1 = self.lazy_wrap('foo')
        obj2 = self.lazy_wrap('bar')
        obj3 = self.lazy_wrap('foo')
        assert obj1 == 'foo'
        assert obj1 == obj3
        assert obj1 != obj2
        assert obj1 != 'bar'

    def test_bytes(self):
        obj = self.lazy_wrap(b'foo')
        assert bytes(obj) == b'foo'

    def test_text(self):
        obj = self.lazy_wrap('foo')
        assert str(obj) == 'foo'

    def test_bool(self):
        # Refs #21840
        for f in [False, 0, (), {}, [], None, set()]:
            assert not self.lazy_wrap(f)
        for t in [True, 1, (1,), {1: 2}, [1], object(), {1}]:
            assert t

    def test_dir(self):
        obj = self.lazy_wrap('foo')
        assert dir(obj) == dir('foo')

    def test_len(self):
        for seq in ['asd', [1, 2, 3], {'a': 1, 'b': 2, 'c': 3}]:
            obj = self.lazy_wrap(seq)
            assert len(obj) == 3

    def test_class(self):
        assert isinstance(self.lazy_wrap(42), int)

        class Bar(Foo):
            pass

        assert isinstance(self.lazy_wrap(Bar()), Foo)

    def test_hash(self):
        obj = self.lazy_wrap('foo')
        d = {obj: 'bar'}
        assert 'foo' in d
        assert d['foo'] == 'bar'

    def test_contains(self):
        test_data = [
            ('c', 'abcde'),
            (2, [1, 2, 3]),
            ('a', {'a': 1, 'b': 2, 'c': 3}),
            (2, {1, 2, 3}),
        ]
        for needle, haystack in test_data:
            assert needle in self.lazy_wrap(haystack)

        # __contains__ doesn't work when the haystack is a string and the needle a LazyObject
        for needle_haystack in test_data[1:]:
            assert self.lazy_wrap(needle) in haystack
            assert self.lazy_wrap(needle) in self.lazy_wrap(haystack)

    def test_getitem(self):
        obj_list = self.lazy_wrap([1, 2, 3])
        obj_dict = self.lazy_wrap({'a': 1, 'b': 2, 'c': 3})

        assert obj_list[0] == 1
        assert obj_list[-1] == 3
        assert obj_list[1:2] == [2]
        assert obj_dict['b'] == 2

        with pytest.raises(IndexError):
            obj_list[3]

        with pytest.raises(KeyError):
            obj_dict['f']

    def test_setitem(self):
        obj_list = self.lazy_wrap([1, 2, 3])
        obj_dict = self.lazy_wrap({'a': 1, 'b': 2, 'c': 3})

        obj_list[0] = 100
        assert obj_list == [100, 2, 3]
        obj_list[1:2] = [200, 300, 400]
        assert obj_list == [100, 200, 300, 400, 3]

        obj_dict['a'] = 100
        obj_dict['d'] = 400
        assert obj_dict == {'a': 100, 'b': 2, 'c': 3, 'd': 400}

    def test_delitem(self):
        obj_list = self.lazy_wrap([1, 2, 3])
        obj_dict = self.lazy_wrap({'a': 1, 'b': 2, 'c': 3})

        del obj_list[-1]
        del obj_dict['c']
        assert obj_list == [1, 2]
        assert obj_dict == {'a': 1, 'b': 2}

        with pytest.raises(IndexError):
            del obj_list[3]

        with pytest.raises(KeyError):
            del obj_dict['f']

    def test_iter(self):
        # Tests whether an object's custom `__iter__` method is being
        # used when iterating over it.

        class IterObject(object):

            def __init__(self, values):
                self.values = values

            def __iter__(self):
                return iter(self.values)

        original_list = ['test', '123']
        assert list(self.lazy_wrap(IterObject(original_list)))== original_list

    def test_pickle(self):
        # See ticket #16563
        obj = self.lazy_wrap(Foo())
        pickled = pickle.dumps(obj)
        unpickled = pickle.loads(pickled)
        assert isinstance(unpickled, Foo)
        assert unpickled == obj
        assert unpickled.foo == obj.foo

    # Test copying lazy objects wrapping both builtin types and user-defined
    # classes since a lot of the relevant code does __dict__ manipulation and
    # builtin types don't have __dict__.

    def test_copy_list(self):
        # Copying a list works and returns the correct objects.
        lst = [1, 2, 3]

        obj = self.lazy_wrap(lst)
        len(lst)  # forces evaluation
        obj2 = copy.copy(obj)

        assert obj is not obj2
        assert isinstance(obj2, list)
        assert obj2 == [1, 2, 3]

    def test_copy_list_no_evaluation(self):
        # Copying a list doesn't force evaluation.
        lst = [1, 2, 3]

        obj = self.lazy_wrap(lst)
        obj2 = copy.copy(obj)

        assert obj is not obj2
        assert obj._wrapped is empty
        assert obj2._wrapped is empty

    def test_copy_class(self):
        # Copying a class works and returns the correct objects.
        foo = Foo()

        obj = self.lazy_wrap(foo)
        str(foo)  # forces evaluation
        obj2 = copy.copy(obj)

        assert obj is not obj2
        assert isinstance(obj2, Foo)
        assert obj2 == Foo()

    def test_copy_class_no_evaluation(self):
        # Copying a class doesn't force evaluation.
        foo = Foo()

        obj = self.lazy_wrap(foo)
        obj2 = copy.copy(obj)

        assert obj is not obj2
        assert obj._wrapped is empty
        assert obj2._wrapped is empty

    def test_deepcopy_list(self):
        # Deep copying a list works and returns the correct objects.
        lst = [1, 2, 3]

        obj = self.lazy_wrap(lst)
        len(lst)  # forces evaluation
        obj2 = copy.deepcopy(obj)

        assert obj is not obj2
        assert isinstance(obj2, list)
        assert obj2 == [1, 2, 3]

    def test_deepcopy_list_no_evaluation(self):
        # Deep copying doesn't force evaluation.
        lst = [1, 2, 3]

        obj = self.lazy_wrap(lst)
        obj2 = copy.deepcopy(obj)

        assert obj is not obj2
        assert obj._wrapped is empty
        assert obj2._wrapped is empty

    def test_deepcopy_class(self):
        # Deep copying a class works and returns the correct objects.
        foo = Foo()

        obj = self.lazy_wrap(foo)
        str(foo)  # forces evaluation
        obj2 = copy.deepcopy(obj)

        assert obj is not obj2
        assert isinstance(obj2, Foo)
        assert obj2 == Foo()

    def test_deepcopy_class_no_evaluation(self):
        # Deep copying doesn't force evaluation.
        foo = Foo()

        obj = self.lazy_wrap(foo)
        obj2 = copy.deepcopy(obj)

        assert obj is not obj2
        assert obj._wrapped is empty
        assert obj2._wrapped is empty


