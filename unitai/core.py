import re
import inspect
import unittest
from copy import copy
from pprint import pprint
from random import random
from typing import List, Type, Dict
from unittest import TestCase

from unitai import MagicFunction, ai_call, magic_functions
from unitai.magic import cleanup_implementation
from unitai.rand import up_to_1
from unitai.tree import create_page_and_open_browser


class State:
    orig_context: str  # all the files at the beginning of the search
    context: str  # the orig_context concatenated with the current implementations from this state
    prompt: str
    ai_output: str
    impls: Dict[str, str]  # For each function, the source-code implementation: func_name -> code implementation.
    mfs: List[MagicFunction]  # the magic functions with their original definitions and "current" implementations
    tests: str  # the source code of the test class
    errors: List[str]  # the errors we got from the tests
    score: float  # the score for this solution
    children: List['State']
    temperature: float = None
    count = None

    def __init__(self):
        self.orig_context: str = ''
        self.context: str = None
        self.prompt: str = None
        self.ai_output: str = None
        self.impls: Dict[str, str] = {}
        self.mfs: List[MagicFunction] = None
        self.tests: str = None
        self.errors: List[str] = []
        self.score: float = None
        self.children: List['State'] = []
        self.temperature: float = None
        self.count = None

    def build_context(self):
        context = self.orig_context
        for mf in self.mfs:
            context += (mf.impl if mf.impl is not None else mf.clean_orig_code) + '\n'
        return context

    def __repr__(self):
        return f'#{self.count}<{self.score}, {len(self.errors)}, {self.temperature:.3f}>'

    def to_dict(self):
        return {
            'count': self.count,
            'context': self.context,
            'prompt': self.prompt,
            'ai_output': self.ai_output,
            'impls': self.impls,
            'mfs': [mf.to_dict() for mf in self.mfs],
            'tests': self.tests,
            'errors': self.errors,
            'score': self.score,
            'temperature': self.temperature,
            'children': [child.to_dict() for child in self.children]
        }


def generate_new_state(count, state: State, temperature: float, test_class) -> State:
    """Generates a new state for program space search"""
    new_state = State()
    new_state.mfs = state.mfs
    new_state.count = count
    new_state.tests = state.tests
    new_state.temperature = temperature
    prompt, resp_text = ai_call(state.mfs, state.context, state.tests, state.errors, temperature)
    new_state.prompt = prompt
    new_state.ai_output = resp_text
    impls = parse_ai_output(resp_text)
    new_state.impls = impls
    print(new_state)
    pprint(impls)
    if len(impls) >= len(state.mfs):
        print(f'Received {len(impls)} implementations, expected {len(state.mfs)}')
        for mf in new_state.mfs:
            if mf.func_name in impls:
                mf.set_impl(cleanup_implementation(impls[mf.func_name]))
            else:
                raise f'Expected implementation for {mf.func_name}'
        new_state.context = new_state.build_context()
        errors, errors_count, score = run_test_class(test_class)
        # Reset implementations:
        for mf in new_state.mfs:
            mf.set_impl(None)
        new_state.errors = errors
        new_state.score = score
    else:
        print('LLM OUTPUT:', resp_text)
        new_state.score = 0
        expected_func_names = ','.join([mf.func_name for mf in new_state.mfs])
        received_func_names = ','.join([k for k, _ in impls.items()])
        new_state.errors = f'Expected implementations for {expected_func_names}. Received instead {received_func_names}'
        print(new_state.errors)
    return new_state


def start_search(mfs: List[MagicFunction], test_class: Type[TestCase], display_tree=True):
    # Check all mfs are registered
    for mf in mfs:
        assert mf in magic_functions, f'{mf} not registered with @unitai'

    # Remove @ai annotations from the function implementation
    clean_context = ''
    for mf in mfs:
        clean_context += mf.clean_orig_code + '\n'

    # Run the tree search
    root, states = search(mfs, test_class)
    best_state = states[0]
    if display_tree:
        create_page_and_open_browser(root)
    return best_state


def search(mfs: List[MagicFunction], test_class: TestCase):
    random_spread = 2
    take_best_n = 3
    max_depth = 10
    max_temperature = 0.7

    # Generate the root state
    root = State()
    root.count = 0
    root.mfs = mfs
    root.temperature = 0.0
    root.tests = inspect.getsource(test_class)
    root.errors = []
    root.score = -1  # root state has no score
    # state.orig_context = orig_context # TODO
    root.context = root.build_context()
    states = [root]

    found = False
    count = 0
    for depth in range(max_depth):
        print('DEPTH', depth)
        new_states = []
        # For each state, generate a bunch of new states feeding back the current test errors
        for state in states:
            # Generate a bunch of rand temperatures, but always try temp=0
            # temperatures = [random() * max_temperature for _ in range(random_spread)]
            temperatures = [up_to_1.pop(0) for _ in range(random_spread)]
            if depth == 0:
                temperatures = [0.0] + temperatures  # always try temp=0 at first

            # Generate a bunch of new states: generate code with LLMs and run the tests to get the score
            for temp in temperatures:
                print('TEMPERATURE', temp)
                count += 1
                new_state = generate_new_state(count, state, temp, test_class)
                state.children.append(new_state)
                new_states.append(new_state)
                if new_state.score == 1:
                    # Early quit
                    print('Found perfect score')
                    found = True
                    break
            if found: break
        states = states + new_states
        states = sorted(states, key=lambda s: random())
        states.sort(key=lambda s: s.score, reverse=True)
        print('SCORES   ', [s for s in states], 'Picking the best', take_best_n)
        states = states[:take_best_n]
        print('SELECTED ', [s for s in states])
        create_page_and_open_browser(root)
        if found: break
    return root, states


def run_test_class(test_class) -> (List[str], float, float):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if result.testsRun == 0:
        raise f"Test class {test_class} has no tests."
    errors_count = len(result.failures) + len(result.errors)
    score = 1 - errors_count / result.testsRun
    error_strings = []
    for test_class, error_str in result.errors + result.failures:
        error_strings.append(cleanup_error_str(error_str))
    return error_strings, errors_count, score


def cleanup_error_str(error_str):
    # Remove every reference to the file path:
    error_str = re.sub(r'File ".*", line', 'line', error_str)
    # Find the line with "eval" and "self.func_name":
    lines = error_str.split('\n')

    # Remove reference to eval(...)
    eval_line = -1
    for i, line in enumerate(lines):
        if 'eval(' in line and '{self.func_name}' in line:
            eval_line = i
            break
    if eval_line > 0:
        # Remove the line with eval(...) and those before and after:
        lines = lines[:eval_line - 1] + lines[eval_line + 2:]

    # Put back together the redacted lines
    error_str = '\n'.join(lines)
    return error_str


def parse_ai_output(t: str) -> Dict:
    # find anything between <implements name="..."> and </implement>
    found = re.findall(r'<implement name="(.+?)">(.*?)</implement>', t, re.DOTALL)
    found_dict = dict(found)
    return found_dict

# def match_indentations(impl_dict: Dict, mfs: List[MagicFunction]) -> Dict:
#     for mf in mfs:
#         if mf.func_name in impl_dict:
#             impl = impl_dict[mf.func_name]
#             match_indentation(mf.orig_code, impl)
#     return impl_dict
#
#
# def match_indentation(orig, gen):
#     orig_lines = orig.split('\n')
#     for line in orig_lines:
#         if 'def ' in line:
#             indent = line.split('def ')[0]
#     gen_lines = gen.split('\n')
#     return '\n'.join([indent + line for line in gen_lines])
