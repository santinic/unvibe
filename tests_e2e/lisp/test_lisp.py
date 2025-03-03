import unittest

from tests_e2e.lisp.lisp import lisp


class TestLisp(unittest.TestCase):
    def test_lisp_interpreter(self):
        class LispInterpreterTestClass(unittest.TestCase):
            def test_calculator(self):
                self.assertEqual(lisp("(+ 1 2)"), 3)
                self.assertEqual(lisp("(* 2 3)"), 6)

            def test_nested(self):
                self.assertEqual(lisp("(* 2 (+ 1 2))"), 6)
                self.assertEqual(lisp("(* (+ 1 2) (+ 3 4))"), 21)

            def test_list(self):
                self.assertEqual(lisp("(list 1 2 3)"), [1, 2, 3])

            def test_call_python_functions(self):
                self.assertEqual(lisp("(range 3)"), [0, 1, 2])
                self.assertEqual(lisp("(sum (list 1 2 3)"), 6)
