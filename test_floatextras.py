import math
import sys
import unittest
from floatextras import *

class TupleTest(unittest.TestCase):
    def assertSameNaN(self, x, y):
        self.assertTrue(isnan(x))
        self.assertTrue(isnan(y))
        self.assertEqual(as_tuple(x), as_tuple(y))
    def test_as_tuple(self):
        self.assertEqual(as_tuple(0), (0, (0,)*52, -1023))
        self.assertEqual(as_tuple(.5), (0, (0,)*52, -1))
        self.assertEqual(as_tuple(-.5), (1, (0,)*52, -1))
        self.assertEqual(as_tuple(3.5), (0, (1,1)+(0,)*50, 1))
        self.assertEqual(as_tuple(float('inf')), (0, (0,)*52, 1024))
        self.assertEqual(as_tuple(float('nan')), (0, (1,)+(0,)*51, 1024))
    def test_from_tuple(self):
        self.assertEqual(from_tuple((0, [0]*52, -1023)), 0)
        self.assertEqual(from_tuple((0, [0]*52, -1)), .5)
        self.assertEqual(from_tuple((1, [0]*52, -1)), -.5)
        self.assertEqual(from_tuple((0, [1,1]+[0]*50, 1)), 3.5)
        self.assertEqual(from_tuple((0, [0]*52, 1024)), float('inf'))
        self.assertTrue(math.isnan(from_tuple((0, [1]+[0]*51, 1024))))
        self.assertTrue(math.isnan(from_tuple((0, [0,1]+[0]*50, 1024))))
        self.assertTrue(math.isnan(from_tuple((0, [0]*51+[1], 1024))))
    def test_nan(self):
        self.assertTrue(isqnan(float('nan')))
        self.assertFalse(issnan(float('nan')))
        self.assertTrue(math.isnan(make_nan(123)))
        self.assertTrue(isqnan(make_nan(123)))
        self.assertFalse(issnan(make_nan(123)))
        self.assertTrue(math.isnan(make_nan(123, quiet=False)))
        self.assertFalse(isqnan(make_nan(123, quiet=False)))
        self.assertTrue(issnan(make_nan(123, quiet=False)))
        self.assertEqual(nan_payload(float('nan')), 0)
        self.assertEqual(nan_payload(make_nan(123)), 123)
        self.assertEqual(nan_payload(make_nan(123, quiet=False)), 123)
        self.assertEqual(nan_payload(make_nan(123, quiet=False, sign=1)), 123)
        self.assertEqual(nan_payload(make_nan('snan123')), 123)
        self.assertRaises(ValueError, make_nan, 12345678901234567890)
        self.assertRaises(ValueError, make_nan, 'nan12345678901234567890')
        self.assertRaises(TypeError, make_nan, 1.5)
        self.assertRaises(ValueError, make_nan, 'a')
        self.assertRaises(ValueError, nan_payload, 1)
        self.assertRaises(ValueError, nan_payload, float('inf'))
        self.assertSameNaN(make_nan(123), make_nan('qNaN123'))
        self.assertSameNaN(make_nan(123, sign=1, quiet=False), make_nan('-sNaN123'))
        self.assertRaises(ValueError, make_nan, 'snan0')
    def test_next(self):
        self.assertEqual(next_plus(0), 5e-324)
        self.assertEqual(next_plus(-5e-324), -0.0)
        self.assertEqual(next_minus(-1), -1.0000000000000002)
        self.assertEqual(next_minus(float('inf')), sys.float_info.max)
        self.assertEqual(next_minus(float('-inf')), float('-inf'))
        self.assertEqual(next_toward(float('-inf'), 0), -sys.float_info.max)
        self.assertSameNaN(next_toward(make_nan(123), 0), make_nan(123))
        self.assertSameNaN(next_toward(float('inf'), make_nan(123)),
                           make_nan(123))
        self.assertSameNaN(next_toward(make_nan(123), make_nan(456)),
                           make_nan(123))
    def test_float_difference(self):
        self.assertEqual(float_difference(1.5, next_minus(next_minus(1.5))), 2)
        self.assertEqual(float_difference(-1.5, next_minus(next_minus(-1.5))),
                         2)
        self.assertEqual(float_difference(float('inf'), float('-inf')),
                         0xffe0000000000000)
        self.assertRaises(ValueError, float_difference, 0, float('nan'))
