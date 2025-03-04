import unittest

from unitai.core import cleanup_error_str, parse_ai_output


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
        impls_dict = parse_ai_output(resp_text)
        self.assertEqual(len(impls_dict), 2)
        self.assertEqual(impls_dict['mul'].strip(), mul.strip())
        self.assertEqual(impls_dict['div'].strip(), div.strip())

    def test_parse_output_deepseek(self):
        resp_text = '''
        <think>
Okay, I need to fix the `is_palindrome` function in the given code. Let me look at what's provided.

First, there's a class `Utils` with a method `is_palindrome`. The current implementation returns `s == s[:-1]`. Hmm, that doesn't seem right. If I take a string like 'racecar', s[:-1] would be 'raceca', which isn't equal to 'racecar'. So this approach is incorrect.

Then, there's another attempt using `s[::-2]`. Wait, in Python, slicing with step -2 would reverse the string. For example, 'hello' reversed is 'olleh', and checking if it equals the original would correctly identify palindromes. But the code uses `s[::-2]`, which might be a typo because the correct syntax is `s[::-1]` for reversing.

So the correct way to check for a palindrome is to compare the string with its reverse. That means the function should return `s == s[::-1]`.

I need to make sure that all test cases pass. For 'racecar', it should return True, and for 'hello', False. Using `s[::-1]` will handle these correctly.

Also, I should check if there are any other issues in the code. The function is a static method now, which is good because it can be called without instances. So the corrected function should replace the incorrect logic with the proper reverse comparison.
</think>

To fix the `is_palindrome` function, we need to correctly compare the string with its reversed version.

<implement name="is_palindrome">
        @staticmethod
        def is_palindrome(s: str):
            return s == s[::-1]
</implement>
'''
        impls_dict = parse_ai_output(resp_text)
        self.assertEqual(len(impls_dict), 1)
        self.assertIn('s == s[::-1]', impls_dict['is_palindrome'])

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
        ret = cleanup_error_str(error_str)
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
        ret = cleanup_error_str(error_str)
        self.assertEqual(type(ret), str)

    # def test_match_indentation(self):
    #     orig = '''
    #     @ai
    #     def fun(a, b):
    #         """Implements addition."""
    #             pass
    #     '''
    #     gen = '''def fun(a, b):
    # """Implements addition."""
    # return a + b'''
    #     expected = '''        def fun(a, b):
    #         """Implements addition."""
    #         return a + b'''
    #     ret = match_indentation(orig, gen)
    #     self.assertEqual(ret, expected)
