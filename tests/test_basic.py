import unittest

import unittestai
from tests.SearchTest import SearchTest
from unittestai import ai


class BasicTests(SearchTest):
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
        self.assertEqual(state.passed_assertions, 3)
        self.assertEqual(state.failed_assertions, 0)
        self.assertEqual(state.executed_assertions, 3)

    def test_sqrt(self):
        @ai
        def sqrt(x):
            """Implements sqrt with Newton's method"""
            pass

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

        state = self.base([sqrt], SqrtTest, display_tree=True)
        self.assertEqual(state.passed_assertions, 10)

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
        def power(x, a):
            """Implements exponentiation x^a"""
            pass

        def pitagora(a, b):
            return sqrt(add(power(a, 2), power(b, 2)))

        class PitagoraTestClass(unittest.TestCase):
            def test_pitagoras(self):
                self.assertAlmostEquals(pitagora(3, 4), 5, 2)
                self.assertAlmostEquals(pitagora(5, 12), 13, 2)
                self.assertAlmostEquals(pitagora(7, 24), 25, 2)

        state = self.base([add, sqrt, power], PitagoraTestClass, display_tree=True)
        self.assertEqual(set([mf.name for mf in state.mes]), set(['add', 'sqrt', 'power']))

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
        self.assertEqual(state.passed_assertions, None)  # plain unittest.
