from utils.decorators import classproperty


class TestClassProperty:
    def test_getter(self):
        class Foo(object):
            foo_attr = 123

            def __init__(self):
                self.foo_attr = 456

            @classproperty
            def foo(cls):
                return cls.foo_attr

        class Bar(object):
            bar = classproperty()

            @bar.getter
            def bar(cls):
                return 123

        assert Foo.foo == 123
        assert Foo().foo == 123
        assert Bar.bar == 123
        assert Bar().bar == 123

    def test_override_getter(self):
        class Foo(object):
            @classproperty
            def foo(cls):
                return 123

            @foo.getter
            def foo(cls):
                return 456

        assert Foo.foo == 456
        assert Foo().foo == 456
