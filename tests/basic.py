import unittest

import unitai
from unitai import ai


class BasicTests(unittest.TestCase):
    def setUp(self):
        unitai.reset()

    def test_cleanup_error_str(self):
        error_str = '''
        Traceback (most recent call last):
          File "/Users/claudio/projects/unitai/tests/basic.py", line 47, in test_pitagoras
            self.assertEqual(pitagoras(3, 4), 5)
                             ^^^^^^^^^^^^^^^
          File "/Users/claudio/projects/unitai/tests/basic.py", line 43, in pitagoras
            return sqrt(add(exp(a, 2), exp(b, 2)))
                            ^^^^^^^^^
          File "/Users/claudio/projects/unitai/unitai/__init__.py", line 54, in __call__
            return eval(f'{self.func_name}(*args, **kwargs)')  # then call it
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          File "<string>", line 1, in <module>
          File "<string>", line 6, in exp
        NameError: name 'mul' is not defined
        '''
        ret = unitai.cleanup_error_str(error_str)
        self.assertEqual(type(ret), str)
        self.assertNotIn('/Users/claudio', ret)
        self.assertIn('NameError: name', ret)

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

        failures_count, score, mf = unitai.find_impl([fun], AdditionTestClass)
        self.assertEqual(failures_count, 0)

    def test_three_functions(self):
        @ai
        def add(a, b):
            """Implements addition."""
            pass

        @ai
        def sqrt(a, b):
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

        failures_count, score, mf = unitai.find_impl([add, sqrt, exp], PitagorasTestClass)
        self.assertEqual(failures_count, 0)
