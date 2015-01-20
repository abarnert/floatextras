# floatextras
Extra functions on the built-in `float` similar to those on `Decimal`.

API
---

    >>> from floatextras import *
    >>> f = -123.456
    >>> as_tuple(f)
	FloatTuple(sign=1, digits=(1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1), exponent=6)
    >>> sign, digits, exponent = as_tuple(f)
	>>> from_tuple((0, digits, exponent+1))
	246.912
    >>> next_minus(f)
	-123.45600000000002
    >>> next_plus(f)
	-123.45599999999999
    >>> next_toward(f, 0)
	-123.45599999999999
	>>> float_difference(1, next_minus(next_minus(1)))
	2
	>>> qnan2 = make_nan(2)
	>>> isnan(qnan2)
	True
	>>> isqnan(qnan2)
	True
	>>> issnan(qnan2)
	False
	>>> nan_payload(qnan2)
	2
	>>> isqnan(float('nan'))
	True
	>>> nan_payload(float('nan'))
	0
    
The functions `as_tuple`, `next_minus`, `next_plus`, and `next_toward`
have the same effect as the corresponding methods on
[`Decimal`][1] objects, but for values of the builtin [`float`][2]
type, and `from_tuple` is equivalent to the `Decimal` constructor from 
a tuple.

  [1]: https://docs.python.org/3/library/decimal.html
  [2]: https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex

The `float_difference` function is an inverse `next_plus`--it tells
you how many times you'd need to call `next_plus` on `g` to get `f`.

The `nan` functions are utility functions to construct and examine NaN
values with specific payloads.

An optional `direct` argument to most functions can be used to force
the module to use [`ctypes`][3] to reinterpret-cast the bits of the
value as stored, instead of encoding it portably using the
[`struct`][4] module. On almost all platforms, this will give the 
same results; on platforms that don't natively use [IEEE floats][5], 
or store them in a different byte order than the primary byte order, 
this will instead give the _wrong_ results (but that may be useful 
to check for while experimenting).

  [3]: https://docs.python.org/3/library/ctypes.html
  [4]: https://docs.python.org/3/library/struct.html
  [5]: http://en.wikipedia.org/wiki/IEEE_floating_point

Differences from Decimal
------------------------

A fixed-size binary float is of course not identical to an
arbitrary-size decimal float. That means the tuple representation is
significantly different. In particular: 

`Decimal` is stored as an integer plus an exponent, with separate
special exponents for infinity, quiet NaN, and signaling NaN (`F`,
`n`, and `N`, respectively).

`float` is stored as a fraction between 1 and 2, with the leading 1
implicit, plus an exponent, with a single special exponent for
infinity and both NaNs (1024, which is infinity if all digits are 0,
otherwise NaN, quiet if the first digit is 1) and another one for zero
and denormal values (-1023, which is treated as -1022 but without the
implicit leading 1 on the fraction).

The differences are easier to see through experimentation than
explanation (which is partly why this module exists).

Motivation
----------

Python's `Decimal` type represents an IEEE 854-1987 decimal float, and 
it comes with a number of handy operations for exploring the details of 
that representation, like the [`next_plus`][6] family and 
[`as_tuple`][6]. And sometimes these operations are useful beyond 
exploration—e.g., to test whether the result of an algorithm is within 
1 ulp of the expected result.

  [6]: https://docs.python.org/3/library/decimal.html#decimal.Decimal.next_plus
  [7]: https://docs.python.org/3/library/decimal.html#decimal.Decimal.as_tuple

However, while the built-in `float` type nearly always represents
an IEEE 754-1985 binary float, for which the same operations would be
handy, they aren't included.

Of course it's possible to get the bits of a `float` and operator on
them manually, as explained in [IEEE Floats and Python][8], it isn't
nearly as convenient.

  [8]: http://stupidpythonideas.blogspot.com/2015/01/ieee-floats-and-python.html
  
So, this module provides similar functions for `float`.
