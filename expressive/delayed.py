from math import floor, ceil, trunc
from operator import pow, not_, abs, index, length_hint, is_

from expressive.single import Const, evaluate, SingleParamExpression, _eq_

__all__ = [
    'Abs', 'All', 'Any', 'Ascii',
    'Bin', 'Bool', 'ByteArray', 'Bytes',
    'Callable', 'Ceil', 'Chr', 'Complex',
    'Dict', 'Dir', 'DivMod',
    'Enumerate', 'Eval',
    'Filter', 'Float', 'Floor', 'Format', 'FrozenSet',
    'GetAttr',
    'HasAttr', 'Hash', 'Hex',
    'Id', 'If', 'In', 'Index', 'Int', 'Is', 'IsInstance', 'IsSubclass', 'Iter',
    'Len', 'LengthHint', 'List',
    'Map', 'Max', 'MemoryView', 'Min',
    'Next', 'Not',
    'Oct', 'Open', 'Ord',
    'Pow', 'Print',
    'Range', 'Repr', 'Reversed',
    'Round',
    'Set', 'SetAttr', 'Slice', 'Sorted', 'Str', 'Sum',
    'Trunc', 'Tuple', 'Type',
    'Vars',
    'Zip'
]

Abs = abs
All = Const(all, 'All')
Any = Const(any, 'Any')
Ascii = Const(ascii, 'Ascii')
Bin = Const(bin, 'Bin')
Bool = Const(bool, 'Bool')
ByteArray = Const(bytearray, 'ByteArray')
Bytes = Const(bytes, 'Bytes')
Callable = Const(callable, 'Callable')
Ceil = ceil
Chr = Const(chr, 'Chr')
Complex = Const(complex, 'Complex')
Dict = Const(dict, 'Dict')
Dir = Const(dir, 'Dir')
DivMod = Const(divmod, 'DivMod')
Enumerate = Const(enumerate, 'Enumerate')
Eval = Const(eval, 'Eval')
Filter = Const(filter, 'Filter')
Float = Const(float, 'Float')
Floor = floor
Format = Const(format, 'Format')
FrozenSet = Const(frozenset, 'FrozenSet')
GetAttr = Const(getattr, 'GetAttr')
HasAttr = Const(hasattr, 'HasAttr')
Hash = Const(hash, 'Hash')
Hex = Const(hex, 'Hex')
Id = Const(id, 'Id')
In = Const(lambda a, b: a in b, 'In')
Index = Const(index, 'Index')
Int = Const(int, 'Int')
Is = Const(is_, 'Is')
IsInstance = Const(isinstance, 'IsInstance')
IsSubclass = Const(issubclass, 'IsSubclass')
Iter = Const(iter, 'Iter')
Len = Const(len, 'Len')
LengthHint = Const(length_hint, 'LengthHint')
List = Const(list, 'List')
Map = Const(map, 'Map')
Max = Const(max, 'Max')
MemoryView = Const(memoryview, 'MemoryView')
Min = Const(min, 'Min')
Next = Const(next, 'Next')
Not = Const(not_, 'Not')
Oct = Const(oct, 'Oct')
Open = Const(open, 'Open')
Ord = Const(ord, 'Ord')
Pow = Const(pow, 'Pow')
Print = Const(print, 'Print')
Range = Const(range, 'Range')
Repr = Const(repr, 'Repr')
Reversed = reversed
Round = round
Set = Const(set, 'Set')
SetAttr = Const(setattr, 'SetAttr')
Slice = slice
Sorted = Const(sorted, 'Sorted')
Str = Const(str, 'Str')
Sum = Const(sum, 'Sum')
Trunc = trunc
Tuple = Const(tuple, 'Tuple')
Type = Const(type, 'Type')
Vars = Const(vars, 'Vars')
Zip = Const(zip, 'Zip')


class If(SingleParamExpression):
    def __init__(self, then, condition, otherwise):
        self.__then = then
        self.__condition = condition
        self.__otherwise = otherwise

    def _evaluate(self, v):
        if evaluate(self.__condition, v):
            return evaluate(self.__then, v)
        return evaluate(self.__otherwise, v)

    def _eq(self, other) -> bool:
        return type(self) is type(other) \
               and _eq_(self.__condition, other.__condition) \
               and _eq_(self.__then, other.__then) \
               and _eq_(self.__otherwise, other.__otherwise)

    def __repr__(self):
        return f'If({self.__then!r}, {self.__condition!r}, {self.__otherwise!r})'
