Expressive
==========
Create single-parameter lambda functions with ease!
```python
from expressive import _, e

# use _ as the parameter when building your expression
inc_expression = _+1
# use e to finalize the expression
inc = e(inc_expression)
assert inc(6) == 7
# you can use expressions in place of lambdas
whole = filter(e(_ % 1 == 0), [1,1.2,1.0,3])
# many builtin functions have delayed counterparts, for use in expressions
from expressive import Abs
ints = sorted([1,5,-3,2,-1.1], key=e(Abs(_)))
# you can even use specialized functional functions for fluent use!
from expressive.specialized import filter_e
assert filter_e(_ >= 0, [-6, 1, 5, 0, 1])
```