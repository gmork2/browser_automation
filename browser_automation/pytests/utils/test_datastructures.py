from utils.datastructures import OrderedSet


class TestOrderedSet:

    def test_bool(self):
        s = OrderedSet()
        assert not s
        s.add(1)
        assert s

    def test_len(self):
        s = OrderedSet()
        assert len(s) == 0
        s.add(1)
        s.add(2)
        s.add(2)
        assert len(s) == 2