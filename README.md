# floatextras
Extra functions on the built-in `float` similar to those on `Decimal`.

API
---

    floatextras.as_tuple(f, *, native=False)
    floatextras.next_minus(f, *, native=False)
    floatextras.next_plus(f, *, native=False)
    floatextras.next_toward(f, g, *, native=False)
    
These functions have the same effect as the corresponding methods on
[`Decimal`][1] objects, but for values of the builtin [`float`][2]
type.

  [1]: https://docs.python.org/3/library/decimal.html
  [2]: https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex

The `native` argument is used to determine whether the module uses
[`ctypes`][3] to directly access the bits of the value as stored, 
instead of encoding it portably using the [`struct`][4] module.
On almost all platforms, this will give the same results; on 
platforms that don't natively use [IEEE floats][5], or store them 
in a different byte order than the primary byte order, this will 
instead give the _wrong_ results (but that may be useful to test 
for).

  [3]: https://docs.python.org/3/library/ctypes.html
  [4]: https://docs.python.org/3/library/struct.html
  [5]: http://en.wikipedia.org/wiki/IEEE_floating_point

Use
---

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
