import unittest

import unittestai
from unittestai import MagicFunction, ai
from unittestai.core import parse_ai_output
from unittestai.magic import remove_indentation, cleanup_implementation

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

    def test_cleanup_implementation(self):
        impl = '''
        @ai
        def is_palindrome(s: str):
            return s == s[::-1]
        '''

        self.assertEqual('\ndef is_palindrome(s: str):\n    return s == s[::-1]\n', cleanup_implementation(impl, MagicFunction))

    def test_deepseek_output(self):
        resp_text = '''
        <think>
Okay, I need to fix the `is_palindrome` function so that it correctly checks if a string is a palindrome. The user mentioned there were some errors when running the tests, specifically an exception about the implementation not being set properly.

First, I'll look at the current implementation. The function is supposed to return True if the string reads the same forwards and backwards. The initial attempt used `s == s[:-1]`, which doesn't seem right because it's comparing the entire string to a slice that excludes the last character. That would only work for strings of length 1, not longer ones.

I remember that checking a palindrome can be done by comparing the string to its reverse. So, using slicing, `s[::-1]` creates the reversed version of the string. Comparing `s == s[::-1]` should correctly determine if it's a palindrome.

Wait, in the error message, there was an exception about the implementation not being set for `is_palindrome`. Maybe the function wasn't properly annotated or something is missing. Oh, right, perhaps the function needs to be decorated with `@ai` so that UnitAI can recognize it as a testable function. So I should make sure that the decorator is correctly applied.

Putting it all together, the corrected function should use slicing to reverse the string and compare it to the original. Also, adding the `@ai` decorator will allow the tests to run properly without throwing exceptions.
</think>

To fix the `is_palindrome` function, we need to correctly check if a string reads the same forwards and backwards.

<implement name="is_palindrome">
        @ai
        def is_palindrome(s: str):
            return s == s[::-1]
</implement>
    '''

        @ai
        def is_palindrome():
            pass

        impl_dict = parse_ai_output(resp_text)
        print(impl_dict['is_palindrome'])
        is_palindrome.set_impl(cleanup_implementation(impl_dict['is_palindrome'], is_palindrome.__class__))
        self.assertEqual(is_palindrome('ciao'), False)
        self.assertEqual(is_palindrome('anna'), True)
