import unittest

from unitai import ai, reset
from unitai.core import start_search


class BasicTests(unittest.TestCase):
    def setUp(self):
        reset()

    def test_addition(self):
        @ai
        def fun(a, b):
            """Implements addition."""
            pass

        class AdditionTestClass(unittest.TestCase):
            def test_addition(self):
                self.assertEqual(fun(1, 1), 2)
                self.assertEqual(fun(1, 2), 3)
                self.assertEqual(fun(2.4, 2.1), 4.5)

        state = start_search([fun], AdditionTestClass)
        self.assertEqual(len(state.errors), 0)
        self.assertEqual(state.score, 1.0)

    def test_three_functions(self):
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

        def pitagoras(a, b):
            return sqrt(add(exp(a, 2), exp(b, 2)))

        class PitagorasTestClass(unittest.TestCase):
            def test_pitagoras(self):
                self.assertEqual(pitagoras(3, 4), 5)
                self.assertEqual(pitagoras(5, 12), 13)
                self.assertEqual(pitagoras(7, 24), 25)

        state = start_search([add, sqrt, exp], PitagorasTestClass, display_tree=True)
        self.assertEqual(state.score, 1)
        self.assertEqual(len(state.errors), 0)
        self.assertEqual(len(state.mfs), 3)
        self.assertEqual(set([mf.func_name for mf in state.mfs]), set(['add', 'sqrt', 'exp']))

    @unittest.skip("Not implemented yet")
    def test_complex_class(self):
        @ai
        class Complex:
            """Implementation of complex numbers in plain Python"""
            pass

        class ComplexTestClass(unittest.TestCase):
            def test_complex_init(self):
                # Test with real and imaginary parts
                c = Complex(3, 4)
                self.assertEqual(c.real, 3)
                self.assertEqual(c.imag, 4)

            def test_complex_str(self):
                # Test string representation
                c1 = Complex(2, 0)
                self.assertEqual(str(c1), '2')
                c2 = Complex(0, 5)
                self.assertEqual(str(c2), '5j')
                c3 = Complex(-1, -6)
                self.assertEqual(str(c3), '-1-6j')

            def test_complex_add(self):
                # Test addition
                c1 = Complex(1, 2)
                c2 = Complex(3, 4)
                result = c1 + c2
                expected = Complex(4, 6)
                self.assertEqual(result.real, expected.real)
                self.assertEqual(result.imag, expected.imag)

            def test_complex_sub(self):
                # Test subtraction
                c1 = Complex(5, 3)
                c2 = Complex(1, -2)
                result = c1 - c2
                expected = Complex(4, 5)
                self.assertEqual(result.real, expected.real)
                self.assertEqual(result.imag, expected.imag)

            def test_complex_mul(self):
                # Test multiplication
                c1 = Complex(2, 3)
                c2 = Complex(4, 5)
                result = c1 * c2
                expected_real = (2 * 4) - (3 * 5)  # Real part is ac - bd
                expected_imag = (2 * 5) + (3 * 4)  # Imaginary part is ad + bc
                self.assertEqual(result.real, expected_real)
                self.assertEqual(result.imag, expected_imag)

            def test_complex_div(self):
                # Test division by a real number
                c1 = Complex(6, 0)
                result = c1 / 2
                expected = Complex(3, 0)
                self.assertEqual(result.real, expected.real)
                self.assertEqual(result.imag, expected.imag)

            def test_conj(self):
                # Test conjugate method
                c = Complex(2, -3)
                result = c.conj()
                self.assertEqual(result.real, 2)
                self.assertEqual(result.imag, 3)

            def test_abs(self):
                # Test absolute value (magnitude)
                c = Complex(3, 4)
                magnitude = abs(c)
                expected = 5.0
                self.assertAlmostEqual(magnitude, expected, delta=1e-6)

            def test_zero(self):
                # Test zero complex number
                z = Complex(0, 0)
                result = str(z)
                self.assertEqual(result, '0')

            def test_large_number(self):
                # Test with large numbers
                c1 = Complex(1e20, -5e30)
                expected_str = f"{c1.real:.1e}+-{abs(c1.imag):.1e}j"
                self.assertEqual(str(c1), expected_str)

            def test_complex_arithmetic_with_zero(self):
                # Test adding zero
                c = Complex(2, 3)
                result = c + Complex(0, 0)
                expected = Complex(2, 3)
                self.assertEqual(result, expected)

        state = start_search([Complex], ComplexTestClass)
        self.assertEqual(state.score, 1)
        self.assertEqual(len(state.errors), 0)

    def test_lisp_interpreter(self):
        @ai
        def lisp(expr):
            """Implements a simple lisp interpreter that uses Python's eval function."""
            pass

        class LispInterpreterTestClass(unittest.TestCase):
            def test_arithmetics(self):
                self.assertEqual(lisp("(+ 1 2)"), 3)
                self.assertEqual(lisp("(* 2 3)"), 6)
                self.assertEqual(lisp("(* 2 (+ 1 2))"), 6)
                self.assertEqual(lisp("(* (+ 1 2) (+ 3 4))"), 21)

            def test_list(self):
                self.assertEqual(lisp("(list 1 2 3)"), [1, 2, 3])

            def test_call_python_functions(self):
                self.assertEqual(lisp("(range 3)"), [0, 1, 2])
                self.assertEqual(lisp("(sum (list 1 2 3)"), 6)

            # def test_import_math(self):
            #     self.assertEqual(lisp("(import math)"), None)
            #     self.assertEqual(lisp("(math.sqrt 4)"), 2)
            #     self.assertEqual(lisp("(math.exp 2 3)"), 8)
            #
            # def test_import_json(self):
            #     self.assertEqual(lisp("(import json)"), None)
            #     self.assertEqual(lisp("(json.loads '{\"x\":1}')"), {"x": 1})

        state = start_search([lisp], LispInterpreterTestClass)
        self.assertGreater(state.score, 1)
        self.assertEqual(len(state.errors), 0)
        self.assertEqual(len(state.mfs), 1)
        self.assertIn(state.mfs[0].func_name, 'lisp')

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

        state = start_search([Utils.is_palindrome], TestIsPalindrome)
        self.assertEqual(state.score, 1)
        self.assertEqual(len(state.errors), 0)
        self.assertEqual(len(state.mfs), 1)
        self.assertIn(state.mfs[0].func_name, 'is_palindrome')
