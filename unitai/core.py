import re
import inspect
import unittest
from copy import copy
from random import random
from typing import List, Type
from unittest import TestCase

from unitai import MagicFunction, ai_call, magic_functions, annotation_text


class State:
    orig_context: str = ''  # all the files at the beginning of the search
    context: str = None  # the orig_context concatenated with the current implementations from this state
    mfs: List[MagicFunction]  # the magic functions with their original definitions and current implementations
    tests: str  # the source code of the test class
    errors: List[str]  # the errors we got from the tests
    score: float  # the score for this solution

    def build_context(self):
        context = self.orig_context
        for mf in self.mfs:
            context += (mf.impl if mf.impl is not None else mf.clean_orig_code) + '\n'
        return context


def generate_new_state(state: State, temperature: float, test_class) -> State:
    """Generates a new state for program space search"""
    new_state = State()
    new_state.mfs = copy(state.mfs)
    resp_text, impls_dict = ai_call(state.mfs, state.context, state.tests, state.errors, temperature)
    if len(impls_dict) == len(state.mfs):
        print(f'{len(impls_dict)} implementations')
        for mf in new_state.mfs:
            if mf.func_name in impls_dict:
                mf.set_impl(impls_dict[mf.func_name])
        new_state.context = new_state.build_context()
        errors, errors_count, score = run_test_class(test_class)
        new_state.errors = errors
        new_state.score = score
    else:
        print('LLM OUTPUT:', resp_text)
        print(f'Model returned {len(impls_dict)} implementations, expected {len(state.mfs)}')
        new_state.score = 0
        new_state.errors = 'No <ouput><implementation>'
    return new_state


def main(source_files, test_files, replace, output_folder):
    # TODO: if is folder, get all files
    source = source_files[0]
    test_file = test_files[0]

    # Read file source and test
    # with open(source, 'r') as f:
    #     source_content = f.read()
    with open(test_file, 'r') as f:
        texst_file_content = f.read()


    start_search(mfs, test_class)


def start_search(mfs: List[MagicFunction], test_class: Type[TestCase]):
    # Check all mfs are registerd
    for mf in mfs:
        assert mf in magic_functions, f'{mf} not registered with @unitai'

    # Remove @ai annotations from the function implementation
    clean_context = ''
    for mf in mfs:
        mf.clean_orig_code = mf.orig_code.replace(annotation_text, '')
        clean_context += mf.clean_orig_code + '\n'

    # Run the tree search
    states = search(mfs, test_class)
    best_state = states[0]
    return best_state


def search(mfs: List[MagicFunction], test_class: TestCase):
    random_spread = 2
    take_best_n = 3
    max_depth = 3
    max_temperature = 1.0

    # Generate the root state
    state = State()
    state.mfs = mfs
    state.tests = inspect.getsource(test_class)
    state.errors = []
    state.score = -1  # root state has no score
    # state.orig_context = orig_context # TODO
    state.context = state.build_context()
    states = [state]

    found = False
    for depth in range(max_depth):
        print('DEPTH', depth)
        new_states = []
        # For each state, generate a bunch of new states feeding back the current test errors
        for state in states:
            # Generate a bunch of rand temperatures, but always try temp=0
            temperatures = [random() * max_temperature for _ in range(random_spread)]
            if depth == 0:
                temperatures = [0.0] + temperatures  # always try temp=0 at first

            # Generate a bunch of new states: generate code with LLMs and run the tests to get the score
            for temp in temperatures:
                print('TEMPERATURE', temp)
                new_state = generate_new_state(state, temp, test_class)
                new_states.append(new_state)
                if new_state.score == 1:
                    # Early quit
                    print('Found perfect score')
                    found = True
                    break
            if found: break
        states = states + new_states
        states.sort(key=lambda s: s.score, reverse=True)
        print('SCORES   ', [s.score for s in states], 'Picking the best', take_best_n)
        states = states[:take_best_n]
        print('SELECTED ', [s.score for s in states])
        if found: break
    return states


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


def match_indentation(orig, gen):
    orig_lines = orig.split('\n')
    for line in orig_lines:
        if 'def ' in line:
            indent = line.split('def ')[0]
    gen_lines = gen.split('\n')
    return '\n'.join([indent + line for line in gen_lines])
