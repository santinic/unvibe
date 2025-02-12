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

        class TestClass(unittest.TestCase):
            def test_addition(self):
                self.assertEqual(fun(1, 1), 2)
                self.assertEqual(fun(1, 2), 3)
                self.assertEqual(fun(2.4, 2.1), 4.5)

        failures_count, score, mf = unitai.find_impl(fun, TestClass)
        self.assertEqual(failures_count, 0)

    def test_swap_impl_and_eval(self):
        @ai
        def fun(a, b):
            """Implements addition."""
            pass

        mf = unitai.MagicFunction(fun)
        code = 'def fun(a,b):\n\treturn a+b'
        mf.swap_impl(code)
        mf.eval()
        self.assertEqual(mf.eval(1, 2), 3)
