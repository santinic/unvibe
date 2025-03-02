import unittest

from unitai import MagicFunction, ai

impl_dict = {
    'add': '\n'
           'def add(a, b):\n'
           '    from decimal import Decimal\n'
           '    return Decimal(str(a)) + Decimal(str(b))\n',
    'exp': '\n'
           'import math as cmath\n'
           'def exp(x, a):\n'
           '    return (cmath.exp(cmath.log(x) * a))\n',
    'sqrt': '\n'
            'from math import sqrt as math_sqrt\n'
            'def sqrt(x):\n'
            '    if x < 0:\n'
            '        raise ValueError("Cannot calculate square root of negative '
            'number")\n'
            '    return math_sqrt(x)\n'}


class TestMagicFunction(unittest.TestCase):
    def test_eval_add(self):
        @ai
        def add(a, b):
            pass

        add.set_impl(impl_dict['add'])
        self.assertEqual(add(2, 3), 5)

    def test_eval_exp(self):
        @ai
        def exp(x, a):
            pass

        exp.set_impl(impl_dict['exp'])
        self.assertAlmostEquals(exp(2, 3), 8)
        self.assertEqual(exp(2, 0), 1)

    def test_eval_sqrt(self):
        @ai
        def sqrt(x):
            pass

        sqrt.set_impl(impl_dict['sqrt'])
        self.assertEqual(sqrt(4), 2)
        self.assertEqual(sqrt(9), 3)
        self.assertEqual(sqrt(16), 4)
