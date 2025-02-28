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

    def test_parse_output_deepseek(self):
        resp_text = '''
        <think>
Okay, so I'm trying to figure out how to solve this problem. The user provided some code with a function called 'fun' that's supposed to implement addition but right now it just has a pass statement. My task is to write the implementation for this function.

First, I'll look at the function definition: def fun(a, b): """Implements addition.""" So, the function takes two arguments, a and b, and it's supposed to return their sum. The docstring says it implements addition, which confirms what I need to do.

I remember that in Python, adding two numbers is straightforward using the '+' operator. So inside the function, I should return a + b. That makes sense because when you add two numbers, you just combine them with plus.

Wait, are there any edge cases I should consider? Like if a or b are not numbers? But since the problem doesn't specify handling errors, maybe I don't need to worry about that right now. The function is supposed to implement addition, so as long as it returns the sum of a and b, it should be correct.

So putting it all together, the function will take a and b, add them using '+', and return the result. That's simple enough. I don't see any other steps needed here because the problem is pretty straightforward.
</think>

<output implement="fun">
def fun(a, b):
    """Implements addition."""
    return a + b
</output>'''
        impls_dict = parse_output(resp_text)
        self.assertEqual(len(impls_dict), 1)
        self.assertIn('a + b', impls_dict['fun'])

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
