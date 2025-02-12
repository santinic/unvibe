import inspect
import sys
import unittest
import re
from pprint import pprint
from unittest import TestCase
from typing import Callable

from .ai import ai_call

magic_functions = []
config = None
annotation_text = '@ai'


def reset():
    magic_functions.clear()


def as_short_code(code, max_len=50):
    short_code = code.replace('\n', ' ').strip()[:max_len]
    short_code = re.sub(r'\s+', ' ', short_code)
    return short_code


class MagicFunction:
    orig_func: Callable
    orig_code: str

    def __init__(self, orig_func: Callable):
        self.orig_func = orig_func
        self.orig_code = inspect.getsource(orig_func)
        self.func_name = orig_func.__name__
        self.impl = None

    def set_impl(self, impl):
        self.impl = impl

    def __repr__(self):
        short_code = as_short_code(self.orig_code)
        return f'MagicFunction({short_code}...)'

    def __call__(self, *args, **kwargs):
        exec(self.impl)  # define the function
        return eval(f'{self.func_name}(*args, **kwargs)')  # then call it


def ai(thing):
    mf = MagicFunction(thing)
    print(f'Adding {mf} to magic_functions')
    magic_functions.append(mf)
    return mf


def find_impl(mf: MagicFunction, test_class: TestCase) -> (float, float, MagicFunction):
    assert mf in magic_functions, f'{mf} not registered with @unitai'

    clean_code = mf.orig_code.replace(annotation_text, '')
    impl = ai_call(mf.func_name, clean_code)
    mf.set_impl(impl)
    print(as_short_code(impl))
    failures_count, score = run_test_class(test_class)
    print('score:', score)
    return failures_count, score, mf


def run_test_class(test_class):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if result.testsRun == 0:
        raise f"Test class {test_class} has no tests."
    failures_count = len(result.failures) + len(result.errors)
    score = 1 - failures_count / result.testsRun
    return failures_count, score


def show_help():
    print('Usage: ')
    print('\tpython unitmagic.py <source folder> <unit-test folder>')
    print('\tpython unitmagic.py <source file> <unit-test file>')
    print('Examples:')
    print('\tpython unitmagic.py src/ tests/')
    print('\tpython unitmagic.py src/main.py test/test_main.py')


def core(src_files, test_files):
    print('Source files:', src_files)
    print('Test files:', test_files)

    # first run to populate func_map
    score = run_tests(test_files)
    print('Score: ', score)


if __name__ == '__main__':
    # get first command line argument
    if len(sys.argv) != 3:
        show_help()
        sys.exit(1)

    src_dir = sys.argv[1]
    test_dir = sys.argv[2]
    core(src_dir, test_dir)
