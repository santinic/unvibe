import unittest

import unitai
from unitai.ai import parse_output


class UtilsTest(unittest.TestCase):
    def test_parse_output(self):
        mul = '''
        def mul(a, b):
            return a * b
        '''
        div = '''
        def div(a, b):
            return a / b
        '''
        resp_text = '''
        <implement name="mul">
        def mul(a, b):
            return a * b
        </implement>
        <implement name="div">
        def div(a, b):
            return a / b
        </implement>
        </output>
        '''
        impls_dict = parse_output(resp_text)
        self.assertEqual(len(impls_dict), 2)
        self.assertEqual(impls_dict['mul'].strip(), mul.strip())
        self.assertEqual(impls_dict['div'].strip(), div.strip())

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
        print(ret)
        self.assertEqual(type(ret), str)
        self.assertNotIn('/Users/claudio', ret)
        self.assertIn('NameError: name', ret)

    def test_cleanup_error_str_2(self):
        error_str = '''
        Traceback (most recent call last):
          File "/Users/claudio/projects/unitai/tests/test_basic.py", line 19, in test_addition
            self.assertEqual(fun(1, 1), 2)
                             ^^^^^^^^^
          File "/Users/claudio/projects/unitai/unitai/magic.py", line 36, in __call__
            assert self.impl is not None, f'Implementation not set for {self}'
                   ^^^^^^^^^^^^^^^^^^^^^
        AssertionError: Implementation not set for MagicFunction(@ai def fun(a, b): """Implements addition.""" pass…...)
        '''
        ret = unitai.cleanup_error_str(error_str)
        self.assertEqual(type(ret), str)

    def test_match_indentation(self):
        orig = '''
        @ai
        def fun(a, b):
            """Implements addition."""
                pass
        '''
        gen = '''def fun(a, b):
    """Implements addition."""
    return a + b'''
        expected = '''        def fun(a, b):
            """Implements addition."""
            return a + b'''
        ret = unitai.match_indentation(orig, gen)
        self.assertEqual(ret, expected)
