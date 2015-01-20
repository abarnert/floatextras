#!/usr/bin/env python3

import collections
import ctypes
from math import isfinite, isinf, isnan
import struct
import sys

version_info = (0, 0, 3)
version = '{}.{}.{}'.format(*version_info)

FloatTuple = collections.namedtuple('FloatTuple',
                                    'sign digits exponent'.split())

def _int_to_bits(n, count):
    if not isinstance(n, int):
        raise TypeError('{!r} is not an integer'.format(n))
    if n < -(1<<(count-1)) or n > (1<<count)-1:
        raise ValueError('Cannot fit {} into {} bits'.format(n, count))
    if n < 0:
        n += (1<<count)
    return tuple(map(int, format(n, '0{}b'.format(count))))

def _int_from_bits(bits):
    return sum(b*(1<<i) for i, b in enumerate(tuple(bits)[::-1]))

def to_bits(f, *, direct=False, bigendian=True):
    """to_bits(f) -> tuple

    Returns a tuple of 64 ints containing the bits of the float f.

    If direct is true, the value will be converted via a ctypes
    "reinterpret cast", instead of by encoding it portably.

    If bigendian is true, the value will be byteswapped to big-endian
    on little-endian platforms.
    """
    
    if direct:
        p = ctypes.POINTER(ctypes.c_double)()
        p.contents = ctypes.c_double(f)
        value = ctypes.cast(p, ctypes.POINTER(ctypes.c_uint64)).contents
        if bigendian:
            value = struct.unpack('>Q', struct.pack('Q', value))[0]
    else:
        if bigendian:
            value = struct.unpack('>Q', struct.pack('>d', f))[0]
        else:
            value = struct.unpack('Q', struct.pack('d', f))[0]
    return _int_to_bits(value, 64)

def from_bits(bits, *, direct=False, bigendian=True):
    """from_bits(bits) -> float

    Returns a float with the (64) bits from the input.

    If direct is true, the value will be converted via a ctypes
    "reinterpret cast", instead of by encoding it portably.

    If bigendian is true, the value will be byteswapped from big-endian
    on little-endian platforms.
    """
    
    value = _int_from_bits(bits)
    if direct:
        if bigendian:
            value = struct.unpack('Q', struct.pack('>Q', value))[0]
        p = ctypes.POINTER(ctypes.c_uint64)()
        p.contents = ctypes.c_uint64(value)
        return ctypes.cast(p, ctypes.POINTER(ctypes.c_double)).contents
    else:
        if bigendian:
            return struct.unpack('>d', struct.pack('>Q', value))[0]
        else:
            return struct.unpack('d', struct.pack('Q', value))[0]

def as_tuple(f, *, direct=False):
    """as_tuple(f) -> (sign, digits, exponent)

    Returns a tuple representation of the number.

    Note that digits does not include the implicit leading 1 digit
    for normal floats.
    """
    bits = to_bits(f, direct=direct)
    sign = bits[0]
    exponent = _int_from_bits(bits[1:12]) - 1023
    digits = bits[12:]
    return FloatTuple(sign, digits, exponent)

def from_tuple(t, *, direct=False):
    """from_tuple((sign, digits, exponent)) -> float

    Return a float corresponding to a tuple representation.

    Note that digits should not include the implicit leading 1 digit
    for normal floats.
    """
    sign, digits, exponent = t
    try:
        digits = tuple(digits)
    except TypeError:
        digits = _int_to_bits(digits, sys.float_info.mant_dig-1)
    exponent = _int_to_bits(exponent + 1023, 11)
    bits = (sign,) + exponent + tuple(digits)
    return from_bits(bits, direct=direct)

def next_minus(f, *, direct=False):
    """next_minus(f) - The largest float that is smaller than the
    given operand.
    """
    if isnan(f):
        return f    
    sign, digits, exponent = as_tuple(f, direct=direct)
    if sign:
        if exponent == sys.float_info.max_exp:
            return f
        elif all(digits):
            exponent += 1
            digits = [0] * len(digits)
        else:
            digits = _int_to_bits(_int_from_bits(digits) + 1, len(digits))
    else:
        if any(digits):
            digits = _int_to_bits(_int_from_bits(digits) - 1, len(digits))
        else:
            if exponent < sys.float_info.min_exp:
                sign = 1
                digits = [0] * len(digits)
                digits[-1] = 1
            else:
                exponent -= 1
                digits = tuple(1 for _ in digits)
    return from_tuple((sign, digits, exponent), direct=direct)

def next_plus(f, *, direct=False):
    """next_plus(f) - The smallest float that is larger than the
    given operand.
    """
    return -next_minus(-f, direct=direct)

def next_toward(f, g, *, direct=False):
    """next_toward(f, g) - The number closest to f in the direction
    of g--or, if f==g, f with the sign set to the be same as g.
    """
    if isnan(f):
        return f
    if isnan(g):
        return g
    if f == g:
        return g
    elif f < g:
        return next_plus(f)
    else:
        # Note that this handles NaN properly
        return next_minus(f)

def float_difference(f, g, *, direct=False):
    """float_difference(f, g) - The difference between f and g in
    bits.

    This tells you how many times you'd need to call next_plus
    on g to reach f (or, if negative, next_minus).
    
    For two numbers with the same sign and exponent, the difference
    between the digits (treated as an unsigned integer) is the
    float_difference.
    
    The largest float with one exponent and the smallest with the
    next larger exponent are one bit apart.
    
    The positive and negative zero values are zero bits apart.

    This corresponds loosely to the reverse of (Harrison-style) ULP.
    In other words, float_difference(f, g) is 1 iff f-g == ULP(r)
    for any real f < r < g, except at infinity.
    """
    if isnan(f) or isnan(g):
        raise ValueError('float_difference to NaN is illegal')
    sf, df, ef = as_tuple(f)
    sg, dg, eg = as_tuple(g)
    if sf:
        return -float_difference(-f, -g)
    if sg:
        return float_difference(f, 0) + float_difference(-g, 0)
    if ef == eg:
        return _int_from_bits(df) - _int_from_bits(dg)
    if ef > eg:
        return (_int_from_bits(df) +
                (1<<(sys.float_info.mant_dig-1)) * (ef - eg) -
                _int_from_bits(dg))
    return -float_difference(g, f)

def make_nan(payload, quiet=1, sign=0, *, direct=False):
    """make_nan(payload, quiet, sign) -> NaN
    make_nan(nan_string) -> NaN
    """
    if isinstance(payload, str):
        if payload[0] == '-':
            sign, payload = 1, payload[1:]
        if payload[0].lower() == 's':
            quiet, payload = 0, payload[1:]
        elif payload[0].lower() == 'q':
            quiet, payload = 1, payload[1:]
        if not payload.lower().startswith('nan'):
            raise ValueError('{!r} is not a NaN string'.format(payload))
        payload = payload[3:]
        payload = int(payload) if payload else 0
    if not payload and not quiet:
        raise ValueError('A signaling NaN cannot have payload 0')
    digits = (int(quiet),) + _int_to_bits(payload, sys.float_info.mant_dig-2)
    return from_tuple((sign, digits, sys.float_info.max_exp), direct=direct)

def issnan(f, *, direct=False):
    """issnan(f) -> bool

    Returns True if x is a signaling NaN, and False otherwise."""
    if not isnan(f):
        return False
    sign, digits, exponent = as_tuple(f, direct=direct)
    return not digits[0]

def isqnan(f, *, direct=False):
    """issnan(f) -> bool

    Returns True if x is a quiet NaN, and False otherwise."""
    if not isnan(f):
        return False
    sign, digits, exponent = as_tuple(f, direct=direct)
    return bool(digits[0])

def nan_payload(f, *, direct=False):
    """nan_payload(f) -> int

    Returns the payload of a NaN float."""
    if not isnan(f):
        raise ValueError('{} is a number, not a NaN'.format(f))
    sign, digits, exponent = as_tuple(f, direct=direct)
    return _int_from_bits(digits[1:])
