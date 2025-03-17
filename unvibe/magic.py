import re
import sys
import inspect
import traceback
from typing import Union, Type

from termcolor import colored

annotation_text = '@ai'

impl_is_none_msg = colored(
    'You are probably running a function with @ai annotation without using Unvibe as runner.\n'
    'To run Unvibe you need to define unit-tests and annotate functions with @ai and then run:\n', 'red')
impl_is_none_msg += (
    '$ unvibe src/ tests/                     # To discover all tests in the tests/\n'
    '$ unvibe src/main.py tests/test_main.py  # To run only the tests in the indicated file')


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


def cleanup_implementation(code, cls: Union[Type['MagicFunction'], Type['MagicClass']]):
    code = remove_indentation(code, cls)
    code = remove_annotation(code)
    return code


def remove_indentation(code, cls):
    lines = code.split('\n')
    indent = ''
    first_def = 'class ' if cls == MagicClass else 'def '
    for line in lines:
        if line.strip().startswith(first_def):
            indent = line.split(first_def)[0]
            break
    ret = []
    for line in lines:
        ret.append(line.removeprefix(indent))
    return '\n'.join(ret)


def remove_annotation(code):
    lines = code.split('\n')
    found = None
    for i, line in enumerate(lines):
        if line.strip() == annotation_text:
            found = i
    if found:
        lines.pop(found)
        return '\n'.join(lines)
    return code


class MagicEntity:
    orig: str
    clean_orig_code: str

    def __init__(self, orig):
        self.orig = orig
        self.orig_code = inspect.getsource(orig)
        self.clean_orig_code = self.orig_code.replace(annotation_text, '')  # remove @ai
        self.name = orig.__name__
        self.impl = None

    def set_impl(self, impl):
        self.impl = impl

    def to_dict(self):
        return {
            'name': self.name,
            'orig_code': self.orig_code,
            'impl': self.impl
        }


class MagicFunction(MagicEntity):
    """
    This is a wrapper for the functions annotated with @ai.
    You can swap the implementation of the MagicFunction and let the Unit-Tests invoke
    the original function, but actually eval the implementation.
    The search algorithm will create many different implementations and invoke
    magic_function.set_impl(code) to set the implementation.
    """

    def __repr__(self):
        short_code = as_short_code(self.orig_code)
        return f'MagicFunction({short_code}...)'

    def __call__(self, *args, **kwargs):
        if self.impl is None:
            raise Exception(f'Implementation not set for {self}.\n\n{impl_is_none_msg}')

        imports, code = split_imports_and_code(self.impl)
        ___eval = eval
        try:
            exec(imports, globals())  # run the imports
            exec(code, globals())  # define the function
        except IndentationError as exc:
            traceback.print_exc()
            print('IndentationError produced with:')
            print('Imports:', imports)
            print('Code:', code)
            sys.exit(1)
        return ___eval(f'{self.name}(*args, **kwargs)')  # then call it


class MagicClass(MagicFunction):
    def __repr__(self):
        short_code = as_short_code(self.orig_code)
        return f'MagicClass({short_code}...)'
