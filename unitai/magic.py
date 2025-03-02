import inspect
import re
from typing import Callable

from termcolor import colored


def as_short_code(code, max_len=150):
    short_code = code.replace('\n', ' ').strip()[:max_len] + '…'
    short_code = re.sub(r'\s+', ' ', short_code)
    return short_code


def split_imports_and_code(impl):
    imports = []
    lines = impl.split('\n')
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if line == '':
            continue
        elif clean_line.startswith('import ') or clean_line.startswith('from '):
            imports.append(line)
        else:
            break
    code = '\n'.join(lines[i:])
    imports = '\n'.join(imports)
    return imports, code


class MagicFunction:
    orig_func: Callable
    orig_code: str
    clean_orig_code: str

    def __init__(self, orig_func: str):
        self.orig_func = orig_func
        self.orig_code = inspect.getsource(orig_func)
        self.func_name = orig_func.__name__
        self.impl = None

    def set_impl(self, impl):
        self.impl = impl

    def has_impl(self):
        return self.impl is not None

    def reset_impl(self):
        self.impl = None

    def __repr__(self):
        short_code = as_short_code(self.orig_code)
        return f'MagicFunction({short_code}...)'

    def __call__(self, *args, **kwargs):
        if self.impl is None:
            msg = colored(
                'You are probably running a function with @ai annotation without using UnitAI.\n'
                'To run UnitAI you need to define unit-tests and annotate functions with @ai and then run:\n', 'red')
            msg += (
                '$ unitai tests/                          # To discover all tests in the tests/ folder\n'
                '$ unitai tests/test_my_test_case.py      # To run only the tests in the indicated file')
            raise Exception(f'Implementation not set for {self}.\n\n{msg}')

        imports, code = split_imports_and_code(self.impl)
        ___eval = eval
        exec(imports, globals())  # run the imports
        exec(code)  # define the function
        return ___eval(f'{self.func_name}(*args, **kwargs)')  # then call it
