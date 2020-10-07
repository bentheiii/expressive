from pytest import raises, mark

from expressive import _, e, In, Str, is_expression, DivMod, Const, Abs


def equivalant(v, *callables):
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
            assert f(v) == result
        else:
            raises(result, f, v)


@mark.parametrize('v', [1, 3, 8, True, 'hi', '', 'hello', [1, 2, 3, 'gy'], 1.5, 1.0])
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
    (_ % 1 == 0, lambda x: x % 1 == 0)
])
def test_op(v, ex, lam):
    if is_expression(ex):
        assert ex._eq(eval(repr(ex)))
    ex = e(ex)
    equivalant(v, lam, ex)
