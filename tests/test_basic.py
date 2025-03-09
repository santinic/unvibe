import traceback
import unittest

import unittestai
from unittestai import ai, reset
from unittestai.core import start_search


class BasicTests(unittest.TestCase):
    def setUp(self):
        reset()

    def base(self, functions, test_class, **kwargs):
        try:
            state = start_search(functions, test_class, **kwargs)
        except Exception as exc:
            traceback.print_exc()
            raise exc
        self.assertEqual(0, len(state.errors))
        self.assertEqual(1.0, state.score)
        self.assertEqual(len(state.mes), len(functions))
        self.assertEqual(set([f.name for f in functions]),
                         set([mf.name for mf in state.mes]))
        return state

    def test_addition(self):
        @ai
        def fun(a, b):
            """Implements addition."""
            pass

        class AdditionTestClass(unittestai.TestCase):
            def test_addition(self):
                self.assertEqual(fun(1, 1), 2)
                self.assertEqual(fun(1, 2), 3)
                self.assertEqual(fun(2.4, 2.1), 4.5)

        state = self.base([fun], AdditionTestClass)

    def test_sqrt(self):
        @ai
        def sqrt(x):
            """Implements sqrt with Newton's method"""
            pass

        import unittest

        class SqrtTest(unittestai.TestCase):
            def test_sqrt_integer(self):
                self.assertEqual(sqrt(4), 2)
                self.assertEqual(sqrt(16), 4)
                self.assertEqual(sqrt(25), 5)
                self.assertEqual(sqrt(36), 6)

            def test_sqrt_float(self):
                self.assertEqual(sqrt(4.0), 2.0)
                self.assertEqual(sqrt(16.0), 4.0)
                self.assertEqual(sqrt(25.0), 5.0)
                self.assertAlmostEquals(sqrt(46.4), 6.81, 2)

            def test_sqrt_zero(self):
                self.assertEqual(sqrt(0), 0)
                self.assertEqual(sqrt(0.0), 0.0)

        self.base([sqrt], SqrtTest, display_tree=True)

    def test_pitagora(self):
        @ai
        def add(a, b):
            """Implements addition."""
            pass

        @ai
        def sqrt(x):
            """Implements sqrt with newton's method"""
            pass

        @ai
        def exp(x, a):
            """Implements exponentiation x^a"""
            pass

        def pitagora(a, b):
            return sqrt(add(exp(a, 2), exp(b, 2)))

        class PitagoraTestClass(unittest.TestCase):
            def test_pitagoras(self):
                self.assertAlmostEquals(pitagora(3, 4), 5)
                self.assertAlmostEquals(pitagora(5, 12), 13)
                self.assertAlmostEquals(pitagora(7, 24), 25)

        state = self.base([add, sqrt, exp], PitagoraTestClass, display_tree=True)
        self.assertEqual(set([mf.name for mf in state.mes]), set(['add', 'sqrt', 'exp']))



    def test_fix_wrong_impl_is_palindrome(self):
        # Utils class to check if it retains indentation
        class Utils:
            @ai
            @staticmethod
            def is_palindrome(s: str):
                return s == s[::-2]

        class TestIsPalindrome(unittest.TestCase):
            def test_is_palindrome(self):
                utils = Utils()
                self.assertTrue(utils.is_palindrome('racecar'))
                self.assertFalse(utils.is_palindrome('hello'))

        state = self.base([Utils.is_palindrome], TestIsPalindrome, display_tree=True)
        self.assertIn(state.mes[0].name, 'is_palindrome')

    def test_bubble_sort_plain_unittest_TestCase(self):
        @ai
        def bubble_sort(l):
            """Implements bubble sort, in pure Python, without using any library."""
            pass

        class TestBubbleSort(unittest.TestCase):
            def test_bubble_sort(self):
                self.assertEqual(bubble_sort([3, 2, 1]), [1, 2, 3])
                self.assertEqual(bubble_sort([4, 2, 1, 3]), [1, 2, 3, 4])
                self.assertEqual(bubble_sort([1, 2, 3, 4]), [1, 2, 3, 4])
                self.assertEqual(bubble_sort([4, 3, 2, 1]), [1, 2, 3, 4])

        state = self.base([bubble_sort], TestBubbleSort)

# def test_import_math(self):
#     self.assertEqual(lisp("(import math)"), None)
#     self.assertEqual(lisp("(math.sqrt 4)"), 2)
#     self.assertEqual(lisp("(math.exp 2 3)"), 8)
#
# def test_import_json(self):
#     self.assertEqual(lisp("(import json)"), None)
#     self.assertEqual(lisp("(json.loads '{\"x\":1}')"), {"x": 1})
