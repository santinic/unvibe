import unittest
import unittestai
from tests.SearchTest import SearchTest
from unittestai import ai


# @unittest.skip("Skip this test")
class TestHard(SearchTest):
    def test_complex_class(self):
        @ai
        class Complex:
            """Implementation of complex numbers in plain Python"""
            pass

        class ComplexTestClass(unittestai.TestCase):
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

            def test_complex_arithmetic_with_zero(self):
                # Test adding zero
                c = Complex(2, 3)
                result = c + Complex(0, 0)
                expected = Complex(2, 3)
                self.assertEqual(result, expected)

        state = self.base([Complex], ComplexTestClass)

    def test_lisp_interpreter(self):
        @ai
        def lisp(exp):
            """Implements a simple lisp interpreter in plain Python, no external libraries.
            Use as many auxiliary functions as needed."""
            pass

        class LispInterpreterTestClass(unittestai.TestCase):
            def test_calculator(self):
                self.assertEqual(lisp("(+ 1 2)"), 3)
                self.assertEqual(lisp("(* 2 3)"), 6)

            def test_nested(self):
                self.assertEqual(lisp("(* 2 (+ 1 2))"), 6)
                self.assertEqual(lisp("(* (+ 1 2) (+ 3 4))"), 21)

            def test_list(self):
                self.assertEqual(lisp("(list 1 2 3)"), [1, 2, 3])

            def test_call_python_functions(self):
                self.assertEqual(lisp("(list (range 3)"), [0, 1, 2])
                self.assertEqual(lisp("(sum (list 1 2 3)"), 6)

        state = self.base([lisp], LispInterpreterTestClass)
        self.assertIn(state.mes[0].name, 'lisp')

