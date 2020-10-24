from collections import ChainMap, Counter
from dataclasses import dataclass
from types import SimpleNamespace
from typing import NamedTuple

from pytest import raises, mark

from expressive import _, e, In, Str, DivMod, Const, Abs, If
from expressive.single import _eq_

namespace = SimpleNamespace  # bpo-42088


def are_equal(a, b):
    # apparently TypeError(1) != TypeError(1)
    try:
        if a == b:
            return True
    except Exception:
        pass
    return repr(a) == repr(b)


def equivalent(v, *callables):
    c_iter = iter(callables)
    f = next(c_iter)
    try:
        result = f(v)
    except Exception as e:
        expect_success = False
        result = type(e)
    else:
        expect_success = True

    while True:
        try:
            f = next(c_iter)
        except StopIteration:
            return

        if expect_success:
            assert are_equal(f(v), result)
        else:
            raises(result, f, v)


class Point(NamedTuple):
    x: int
    y: int


@dataclass
class Point3:
    x: int
    y: int
    z: int


@dataclass(frozen=True)
class Point3F:
    x: int
    y: int
    z: int


@mark.parametrize('v', [1, 3, 8, True, 'hi', '', 'hello', [1, 2, 3, 'gy'],
                        1.5, 1.0, {'a': 1, 'b': 2}, {}, 0, -1.0, None])
@mark.parametrize('ex, lam', [
    (_, lambda x: x),
    (_ + _, lambda x: x + x),
    (_ + 1, lambda x: x + 1),
    (1 + _, lambda x: 1 + x),
    (_ + '1', lambda x: x + '1'),
    ('1' + _, lambda x: '1' + x),
    (_.lower(), lambda x: x.lower()),
    (1, lambda x: 1),
    (_[1], lambda x: x[1]),
    (_[1:2], lambda x: x[1:2]),
    (Str(_), str),
    (In(_, 1), lambda x: x in 1),
    (DivMod(_, 2), lambda x: divmod(x, 2)),
    (divmod(_, 2), lambda x: divmod(x, 2)),
    (Const('hi there')[_:], lambda x: 'hi there'[x:]),
    (Abs(-_), lambda x: abs(-x)),
    ((_, _ * _), lambda x: (x, x * x)),
    (_ % 1 == 0, lambda x: x % 1 == 0),
    (_['a'], lambda x: x['a']),
    ([_, 1, 2], lambda x: [x, 1, 2]),
    (TypeError(_, 12), lambda x: TypeError(x, 12)),
    (SimpleNamespace(a=1, b=_ + _), lambda x: SimpleNamespace(a=1, b=x + x)),
    (If('yes', _, 'no'), lambda x: 'yes' if x else 'no'),
    (ChainMap({'x': 1}, _), lambda x: ChainMap({'x': 1}, x)),
    (Counter(a=_), lambda x: Counter(a=x)),
    (Point(_, _), lambda x: Point(x, x)),
    (Point3(_, _, _), lambda x: Point3(x, x, x)),
    (Point3F(_, _, _), lambda x: Point3F(x, x, x)),
])
def test_op(v, ex, lam):
    evaled = eval(repr(ex))
    assert _eq_(ex, evaled)
    ex = e(ex)
    equivalent(v, lam, ex)
