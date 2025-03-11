import inspect
import unittest

from unittestai import TestCase, ai
from unittestai.TestsContainer import count_assertions
from unittestai.core import cleanup_error_str, parse_ai_output, remove_extra_indentation
from unittestai.magic import cleanup_implementation, MagicClass


class CoreTest(unittest.TestCase):

    # def test_run_tests_with_test_suite(self):
    #     class MyTestClass(unittest.TestCase):
    #         def test_one(self):
    #             self.assertEqual(3 + 4, 7)
    #             self.assertEqual(3 + 3, 6)
    #
    #         def test_two(self):
    #             self.assertEqual(1 + 1, 1)
    #             self.assertEqual(2 + 2, 4)
    #
    #     test_suite = unittest.TestLoader().loadTestsFromTestCase(MyTestClass)
    #     error_strings, error_count, score = run_tests(test_suite)
    #     self.assertEqual(error_count, 0)
    #     self.assertEqual(score, 1.0)

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

    def test_cleanup_error_str_3(self):
        error_str = '''
        Traceback (most recent call last):
  line 198, in test_calculator
    self.assertEqual(lisp("(+ 1 2)"), 3)
                     ^^^^^^^^^^^^^^^
  line 102, in __call__
    exec(code)  # define the function
    ^^^^^^^^^^
        :return: 
        '''
        ret = cleanup_error_str(error_str)
        self.assertNotIn('exec(code)', ret)
        self.assertNotIn('__call__', ret)

    def test_cleanup_error_str_4(self):
        error_str = '''
        Traceback (most recent call last):
  line 206, in test_list
  line 111, in __call__
    return ___eval(f'{self.name}(*args, **kwargs)')  # then call it
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  line 1, in <module>
  line 13, in lisp
UnboundLocalError: cannot access local variable 'parse_token' where it is not associated with a value
        '''
        ret = cleanup_error_str(error_str)
        self.assertNotIn('__eval(', ret)
        self.assertNotIn('^^^^^^^^^^^^^^^^^^^^', ret)

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

    def test_count_assertions(self):
        def lisp():
            pass

        class LispInterpreterTestClass(TestCase):
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

        src = inspect.getsource(LispInterpreterTestClass)
        self.assertEqual(count_assertions(src), 7)

    def test_remove_extra_indentation(self):
        code = '''
        class Complex:
            pass

'''
        fixed = remove_extra_indentation(code)
        self.assertEqual(fixed.split('\n')[1], 'class Complex:')
        self.assertEqual(fixed.split('\n')[2], '    pass')

    def test_ai_output_cleanup_magic_class(self):
        ai_output = '''
<implement name="Complex">
class Complex:
    def __init__(self, real=0, imag=0):
        self.real = real
        self.imag = imag
    
    def __str__(self):
        if self.imag >= 0:
            return f"{self.real}+{abs(self.imag)}j"
        else:
            return f"{self.real}{self.imag}j"

    def __add__(self, other):
        if isinstance(other, Complex):
            real = self.real + other.real
            imag = self.imag + other.imag
            return Complex(real, imag)
        elif isinstance(other, (int, float)):
            real = self.real + other
            imag = self.imag
            return Complex(real, imag)
        else:
            raise TypeError("Unsupported operand type for +")

    def __sub__(self, other):
        if isinstance(other, Complex):
            real = self.real - other.real
            imag = self.imag - other.imag
            return Complex(real, imag)
        elif isinstance(other, (int, float)):
            real = self.real - other
            imag = self.imag
            return Complex(real, imag)
        else:
            raise TypeError("Unsupported operand type for -")

    def __mul__(self, other):
        if isinstance(other, Complex):
            real = (self.real * other.real) - (self.imag * other.imag)
            imag = (self.real * other.imag) + (self.imag * other.real)
            return Complex(real, imag)
        elif isinstance(other, (int, float)):
            real = self.real * other
            imag = self.imag * other
            return Complex(real, imag)
        else:
            raise TypeError("Unsupported operand type for *")

    def __truediv__(self, other):
        if isinstance(other, Complex):
            denominator = other.real**2 + other.imag**2
            real = (self.real * other.real + self.imag * other.imag) / denominator
            imag = (self.imag * other.real - self.real * other.imag) / denominator
            return Complex(real, imag)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            real = self.real / other
            imag = self.imag / other
            return Complex(real, imag)
        else:
            raise TypeError("Unsupported operand type for /")

    def conj(self):
        return Complex(self.real, -self.imag)

    @staticmethod
    def abs(c):
        if isinstance(c, Complex):
            return (c.real**2 + c.imag**2)**0.5
        elif isinstance(c, (int, float)):
            return abs(c)
        else:
            raise TypeError("Unsupported operand type for abs")

</implement>
        '''

        @ai
        class Complex:
            pass

        impls = parse_ai_output(ai_output)
        Complex.set_impl(cleanup_implementation(impls['Complex'], MagicClass))
        lines = Complex.impl.split('\n')
        self.assertEqual(lines[1], 'class Complex:')
        self.assertEqual(lines[2], '    def __init__(self, real=0, imag=0):')
