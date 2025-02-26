import unittest

import unitai
from unitai import ai


class BasicTests(unittest.TestCase):
    def setUp(self):
        unitai.reset()

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

        state = unitai.start_search([fun], AdditionTestClass)
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

        failures_count, score, mf = unitai.start_search([add, sqrt, exp], PitagorasTestClass)
        self.assertEqual(failures_count, 0)

    def test_complex_class(self):
        @ai
        class Complex:
            """Implementation of complex numbers"""
            pass

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

            def test_import_math(self):
                self.assertEqual(lisp("(import math)"), None)
                self.assertEqual(lisp("(math.sqrt 4)"), 2)
                self.assertEqual(lisp("(math.exp 2 3)"), 8)

            def test_import_json(self):
                self.assertEqual(lisp("(import json)"), None)
                self.assertEqual(lisp("(json.loads '{\"x\":1}')"), {"x": 1})

        failures_count, score, mf = unitai.start_search([lisp], LispInterpreterTestClass)
        self.assertEqual(failures_count, 0)


