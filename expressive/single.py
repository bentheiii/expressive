from __future__ import annotations

from abc import ABC, abstractmethod
from collections import ChainMap, Counter
from dataclasses import is_dataclass, fields
from functools import singledispatch
from itertools import starmap
from math import floor, ceil, trunc
from operator import \
    add, sub, mul, truediv, floordiv, mod, pow, matmul, lshift, rshift, ge, gt, le, lt, eq, ne, or_, and_, xor, \
    abs, invert, neg, pos
from textwrap import dedent
from types import SimpleNamespace
from typing import Any, Callable, Union, Optional, Iterable, Collection, Mapping


def _eq_(a, b):
    if is_expression(a):
        return a._eq(b)
    if is_expression(b):
        return b._eq(a)
    if not (is_possible_expression(a) or is_possible_expression(b)):
        return a == b
    if hasattr(a, '_fields') and hasattr(b, '_fields'):
        return type(a) is type(b) \
               and _eq_(
            [getattr(a, field) for field in a._fields],
            [getattr(b, field) for field in b._fields],
        )
    if isinstance(a, ChainMap) and isinstance(b, ChainMap):
        return type(a) is type(b) and _eq_(a.maps, b.maps)
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        return type(a) is type(b) and len(a) == len(b) and all(_eq_(b.get(k, object()), v) for (k, v) in a.items())
    if isinstance(a, Collection) and isinstance(b, Collection):
        return type(a) is type(b) and len(a) == len(b) and all(starmap(_eq_, zip(a, b)))
    if isinstance(a, Exception) and isinstance(b, Exception):
        return type(a) is type(b) and _eq_(a.args, b.args)
    if isinstance(a, SimpleNamespace) and isinstance(b, SimpleNamespace):
        return type(a) is type(b) and _eq_(a.__dict__, b.__dict__)
    return a == b


class SingleParamExpression(ABC):
    @abstractmethod
    def _evaluate(self, v):
        pass

    def __getattr__(self, item):
        if item.startswith('__') and not item.endswith('_'):
            raise AttributeError(item)
        return GetAttr(self, item)

    def __bool__(self):
        raise TypeError('an unevaluated expression cannot be used as boolean')

    def __call__(self, *args, **kwargs):
        return Call(self, *args, **kwargs)

    for b_op, op_str in ((add, '+'),
                         (sub, '-'),
                         (mul, '*'),
                         (truediv, '/'),
                         (floordiv, '//'),
                         (mod, '%'),
                         (pow, '**'),
                         (matmul, '@'),
                         (lshift, '<<'),
                         (rshift, '>>'),
                         (or_, '|'),
                         (and_, '&'),
                         (xor, '^'),):
        op = b_op.__name__
        op_name = op.strip('_')
        exec(dedent(f"""
            def __{op_name}__(self, other):
                return BinOp({op_str!r},{op}, self, other)
            def __r{op_name}__(self, other):
                return BinOp({op_str!r},{op}, other, self)
        """))

    for b_op, op_str in ((ge, '>='),
                         (gt, '>'),
                         (le, '<='),
                         (lt, '<'),
                         (eq, '=='),
                         (ne, '!='),):
        op = b_op.__name__
        op_name = op.strip('_')
        exec(dedent(f"""
            def __{op_name}__(self, other):
                return BinOp({op_str!r},{op}, self, other)
        """))

    for u_op, op_str in ((invert, '~'),
                         (neg, '-'),
                         (pos, '+'),):
        op = u_op.__name__
        op_name = op.strip('_')
        exec(dedent(f"""
            def __{op_name}__(self):
                return UnOp({op_str!r},{op}, self)
        """))

    for u_func in (abs,
                   ceil,
                   floor,
                   trunc,
                   round,
                   reversed):
        op = u_func.__name__
        op_name = op.strip('_')
        exec(dedent(f"""
            def __{op_name}__(self):
                return Call({op}, self)
        """))

    def __divmod__(self, other):
        return Call(divmod, self, other)

    def __getitem__(self, item):
        return GetItem(self, item)

    @abstractmethod
    def _eq(self, other) -> bool:
        pass


class Const(SingleParamExpression):
    def __init__(self, c, name=None):
        self.__c = c
        self.__name = name

    def _evaluate(self, v):
        return self.__c

    def __repr__(self):
        if self.__name:
            return self.__name
        return f'Const({self.__c!r})'

    def _eq(self, other) -> bool:
        return type(self) is type(other) \
               and self.__c == other.__c


class BinOp(SingleParamExpression):
    def __init__(self, op_str: str, op: Callable[[Any, Any], Any], lhs, rhs):
        self.__op = op
        self.__op_str = op_str
        self.__lhs = lhs
        self.__rhs = rhs

    def _evaluate(self, v):
        lhs = evaluate(self.__lhs, v)
        rhs = evaluate(self.__rhs, v)
        return self.__op(lhs, rhs)

    def __repr__(self):
        return repr(self.__lhs) + ' ' + self.__op_str + ' ' + repr(self.__rhs)

    def _eq(self, other) -> bool:
        return type(self) is type(other) \
               and self.__op == other.__op \
               and _eq_(self.__lhs, other.__lhs) \
               and _eq_(self.__rhs, other.__rhs)


class UnOp(SingleParamExpression):
    def __init__(self, op_str: str, op: Callable[[Any], Any], inner):
        self.__op = op
        self.__op_str = op_str
        self.__inner = inner

    def _evaluate(self, v):
        inner = evaluate(self.__inner, v)
        return self.__op(inner)

    def __repr__(self):
        return self.__op_str + repr(self.__inner)

    def _eq(self, other) -> bool:
        return type(self) is type(other) \
               and self.__op == other.__op \
               and _eq_(self.__inner, other.__inner)


class Call(SingleParamExpression):
    def __init__(self, op: Union[Callable, SingleParamExpression], *args: Any, **kwargs: Any):
        self.__args = args
        self.__kwargs = kwargs
        self.__op = op

    def _evaluate(self, v):
        args = tuple(evaluate(arg, v) for arg in self.__args)
        kwargs = {k: evaluate(arg, v) for k, arg in self.__kwargs.items()}
        op = evaluate(self.__op, v)
        return op(*args, **kwargs)

    def __repr__(self):
        args = [repr(a) for a in self.__args]
        args.extend(
            [f'{k}={repr(v)}' for (k, v) in self.__kwargs.items()]
        )
        if is_possible_expression(self.__op):
            op = repr(self.__op)
        else:
            op = self.__op.__name__
        return op + '(' + ', '.join(args) + ')'

    def _eq(self, other) -> bool:
        return type(self) is type(other) \
               and _eq_(self.__op, other.__op) \
               and len(self.__args) == len(other.__args) \
               and all(_eq_(s, o) for (s, o) in zip(self.__args, other.__args)) \
               and len(self.__kwargs) == len(other.__kwargs) \
               and self.__kwargs.keys() == other.__kwargs.keys() \
               and all(_eq_(v, other.__kwargs[k]) for (k, v) in self.__kwargs.items())


class GetItem(SingleParamExpression):
    def __init__(self, container, item):
        self.__container = container
        self.__item = item

    def _evaluate(self, v):
        container = evaluate(self.__container, v)
        item = evaluate(self.__item, v)
        return container[item]

    def __repr__(self):
        return repr(self.__container) + '[' + repr(self.__item) + ']'

    def _eq(self, other) -> bool:
        return type(self) is type(other) \
               and _eq_(self.__container, other.__container) \
               and _eq_(self.__item, other.__item)


class GetAttr(SingleParamExpression):
    def __init__(self, parent, attr: str):
        self.__parent = parent
        self.__attr = attr

    def _evaluate(self, v):
        parent = evaluate(self.__parent, v)
        return getattr(parent, self.__attr)

    def __repr__(self):
        return repr(self.__parent) + '.' + self.__attr

    def _eq(self, other) -> bool:
        return type(self) is type(other) \
               and _eq_(self.__parent, other.__parent) \
               and _eq_(self.__attr, other.__attr)


class _Parameter(SingleParamExpression):
    def _evaluate(self, v):
        return v

    def __repr__(self):
        return '_'

    def _eq(self, other) -> bool:
        return type(self) == type(other)


def _evaluate_by_element(self: Iterable, v) -> Optional[list]:
    ret = []
    diffs = False
    for a in self:
        b = evaluate(a, v)
        diffs |= not _eq_(a, b)
        ret.append(b)
    return ret if diffs else None


@singledispatch
def evaluate(self, v):
    field_names = None

    if is_dataclass(self) and not isinstance(self, type):
        field_names = [f.name for f in fields(self)]
    elif hasattr(self, '_fields'):
        field_names = self._fields

    if field_names:
        values = [getattr(self, field) for field in field_names]
        args = _evaluate_by_element(values, v)
        return type(self)(**dict(zip(field_names, args))) if args else self

    return self


@evaluate.register
def _(self: SingleParamExpression, v):
    return self._evaluate(v)


@evaluate.register
def _(self: list, v):
    return _evaluate_by_element(self, v) or self


@evaluate.register
def _(self: tuple, v):
    args = _evaluate_by_element(self, v)
    if not args:
        return self
    if hasattr(self, '_make'):  # _make exists for namedtuples
        return self._make(args)
    return tuple(args)


@evaluate.register
def _(self: slice, v):
    return slice(
        evaluate(self.start, v),
        evaluate(self.stop, v),
        evaluate(self.step, v)
    )


@evaluate.register
def _(self: dict, v):
    tuples = _evaluate_by_element(self.items(), v)
    return dict(tuples) if tuples else self


@evaluate.register
def _(self: BaseException, v):
    args = _evaluate_by_element(self.args, v)
    return type(self)(*args) if args else self


@evaluate.register
def _(self: SimpleNamespace, v):
    args = _evaluate_by_element(self.__dict__.items(), v)
    return SimpleNamespace(**dict(args)) if args else self


@evaluate.register
def _(self: ChainMap, v):
    args = _evaluate_by_element(self.maps, v)
    return ChainMap(*args) if args else self


@evaluate.register
def _(self: Counter, v):
    args = _evaluate_by_element(self.items(), v)
    return Counter(dict(args)) if args else self


class _Evaluated:
    def __init__(self, spe):
        self.spe = spe

    def __call__(self, v):
        return evaluate(self.spe, v)

    def __repr__(self):
        return f'e({self.spe!r})'


def e(spe):
    if isinstance(spe, _Evaluated):
        return spe
    return _Evaluated(spe)


def is_possible_expression(v):
    return evaluate.dispatch(type(v)) != evaluate.dispatch(object) \
           or hasattr(v, '_fields') \
           or (is_dataclass(v) and not isinstance(v, type))


def is_expression(v):
    return isinstance(v, SingleParamExpression)


_ = _Parameter()
