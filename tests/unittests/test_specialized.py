from pytest import mark

from expressive import _, Int
from expressive.specialized import *


@mark.skipif("sys.version_info < (3,9,0)")
def test_cache():
    f = cache_e(_.inc())

    class A:
        def __init__(self):
            self.calls = 0

        def inc(self):
            self.calls += 1

    a = A()
    f(a)
    assert a.calls == 1
    f(a)
    assert a.calls == 1


@mark.skipif("sys.version_info < (3,8,0)")
def test_cached_property():
    class A:
        def __init__(self):
            self.calls = []

        x = cached_property_e(_.calls.append('a'))

    a = A()
    assert a.x is None
    assert a.calls == ['a']
    assert a.x is None
    assert a.calls == ['a']


def test_classmethod():
    class A:
        _x = 1

        x = classmethod_e(_._x)

    A._x = 1
    assert A.x() == 1


def test_dropwhile():
    assert list(dropwhile_e(_ >= 5, [6, 5, 2, 4, 6, 1, 3])) == [2, 4, 6, 1, 3]


def test_filter():
    assert list(filter_e(_ >= 5, [6, 5, 2, 4, 6, 1, 3])) == [6, 5, 6]


def test_filterfalse():
    assert list(filterfalse_e(_ >= 5, [6, 5, 2, 4, 6, 1, 3])) == [2, 4, 1, 3]


def test_groupby():
    assert [(k, tuple(v)) for (k, v) in groupby_e(['wow', 'hi', 'hello', 'world'], _[0])] == [
        ('w', ('wow',)),
        ('h', ('hi', 'hello')),
        ('w', ('world',))
    ]


def list_sort():
    a = ['12', '65', '2']
    list_sort_e(a, key=Int(_))
    assert a == ['2', '12', '65']


def test_lru_cache():
    f = lru_cache_e()(_.inc())

    class A:
        def __init__(self):
            self.calls = 0

        def inc(self):
            self.calls += 1

    a = A()
    f(a)
    assert a.calls == 1
    f(a)
    assert a.calls == 1


def test_map():
    assert list(map_e(_ * _, range(5))) == [0, 1, 4, 9, 16]


def test_max():
    a = [9, 3, 18, 101]
    assert max_e(a, key=_ % 10) == 9
    assert max_e(*a, key=_ % 10) == 9


def test_min():
    a = [9, 3, 18, 101]
    assert min_e(a, key=_ % 10) == 101
    assert min_e(*a, key=_ % 10) == 101


def test_partial():
    assert partial_e(_ + 9, 10)() == 19


def test_property():
    class A:
        def __init__(self, x):
            self.x = x

        y = property_e(_.x ** 2)

    assert A(6).y == 36


def test_singledispatch():
    s = singledispatch_e(_ * 2)
    singledispatch_register_e(s, int, 3 * _)
    singledispatch_register_e(s, float)(_ * 4)

    @s.register(complex)
    def __(x):
        return 5 * x

    assert s('a') == 'aa'
    assert s(6) == 18
    assert s(2.5) == 10.0
    assert s(1 + 1j) == 5 + 5j


def test_sorted():
    assert sorted_e(
        ['hi', 'show', 'gee'],
        key=_[-1]) == ['gee', 'hi', 'show']


def test_takewhile():
    assert list(takewhile_e(
        _.startswith('a'),
        ['abca', 'a banana', 'owl', 'af']
    )) == ['abca', 'a banana']
