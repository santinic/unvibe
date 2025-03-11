import inspect
import re
import traceback
import unittest
from pprint import pprint
from random import random
from typing import List, Dict, Union
from unittest import TestCase, TestSuite, TestLoader

from unittestai import ai_call, magic_entities
from unittestai.config import config, config_get_or
from unittestai.log import log
from unittestai.magic import cleanup_implementation, MagicEntity
from unittestai.rand import up_to_1
from unittestai.state import State
from unittestai.suite import CountingTestSuite
from unittestai.ui import create_page_and_open_browser


def generate_new_state(count, state: State, temperature: float, test_suite: TestSuite) -> State:
    """Generates a new state for program space search"""
    new_state = State()
    new_state.mes = state.mes
    new_state.count = count
    new_state.tests = state.tests
    new_state.temperature = temperature
    if state.context.strip() == '':
        log('Context is empty, skipping state')
        return None
    prompt, resp_text = ai_call(state.mes, state.context, state.tests, state.errors, temperature)
    new_state.prompt = prompt
    new_state.ai_output = resp_text
    impls = parse_ai_output(resp_text)
    new_state.impls = impls
    pprint(impls)
    if len(impls) >= len(state.mes):
        log(f'Received {len(impls)} implementations, expected {len(state.mes)}')
        for me in new_state.mes:
            if me.name in impls:
                cleaned_up = cleanup_implementation(impls[me.name], me.__class__)
                me.set_impl(cleaned_up)
            else:
                raise f'Expected implementation for {me.name}'
        new_state.context = new_state.build_context()
        errors, errors_count, passed_assertions, total_assertions, score = run_tests(test_suite)
        new_state.passed_assertions = passed_assertions
        new_state.total_assertions = total_assertions
        new_state.errors = errors
        new_state.score = score
        # Reset implementations:
        for me in new_state.mes:
            me.set_impl(None)
    else:
        log('LLM OUTPUT:', resp_text)
        new_state.score = 0
        expected_func_names = ','.join([me.name for me in new_state.mes])
        received_func_names = ','.join([k for k, _ in impls.items()])
        new_state.errors = [f'Expected implementations for {expected_func_names}. Received instead [{received_func_names}]']
        log(new_state.errors)
        return None
    return new_state


def start_search(mes: List[MagicEntity], test_suite: TestSuite, display_tree=True):
    log('Using model', config['ai']['model'])

    # Check all magic entities are registered
    for me in mes:
        assert me in magic_entities, f'{me} not registered with @unitai'

    # Remove @ai annotations from the function implementation
    clean_context = ''
    for me in mes:
        clean_context += me.clean_orig_code + '\n'

    # Run the tree search
    root, states = search(mes, test_suite)
    best_state = states[0]
    if display_tree:
        file = create_page_and_open_browser(root)
        print(f'Created execution report {file}')
    return best_state


def get_temperatures():
    random_spread = config_get_or('search', 'random_spread', 2)
    random_type = config_get_or('search', 'random_type', 'increasing')
    max_temperature = config_get_or('search', 'max_temperature', 0.7)

    # Generate a bunch of rand temperatures, but always try temp=0
    if random_type == 'increasing':
        return [up_to_1.pop(0) for _ in range(random_spread)]
    elif random_type == 'uniform':
        return [random() * max_temperature for _ in range(random_spread)]
    else:
        raise f'Unknown random_type "{random_type}". Use either "increasing" or "uniform"'
    return [0.0] + temperatures  # always try temp=0 at first


def search(mes: List[MagicEntity], test_suite: TestSuite):
    take_best_n = config_get_or('search', 'take_best_n', 3)
    max_depth = config_get_or('search', 'max_depth', 10)

    # Generate the root state
    root = State()
    root.count = 0
    root.mes = mes
    root.temperature = 0.0
    root.tests = inspect.getsource(test_suite)
    root.errors = []
    root.score = -1  # root state has no score
    # state.orig_context = orig_context # TODO
    root.context = root.build_context()
    states = [root]

    found = False
    count = 0
    for depth in range(max_depth):
        log('Depth', depth)
        new_states = []
        # For each state, generate a bunch of new states feeding back the current test errors
        for state in states:
            # Generate a bunch of new states: generate code with LLMs and run the tests to get the score
            for temp in get_temperatures():
                log('Temperature', temp)
                count += 1
                new_state = generate_new_state(count, state, temp, test_suite)
                if state is None:
                    continue
                state.children.append(new_state)
                new_states.append(new_state)
                if new_state.score == 1:
                    # Early quit
                    log('Found perfect score')
                    found = True
                    break
            if found: break
        states = states + new_states
        states = sorted(states, key=lambda s: random())
        states.sort(key=lambda s: s.score, reverse=True)
        log('Scores   ', [s for s in states], 'Picking the best', take_best_n)
        states = states[:take_best_n]
        log('Selected ', [s for s in states])
        create_page_and_open_browser(root)
        if found: break
    return root, states


def run_tests(test_union: Union[TestSuite, TestCase]) -> (List[str], int, int, int, float):
    if issubclass(test_union, TestCase):
        # In case you pass just a TestCase (like in tests/), we create a TestSuite out of it:
        loader = TestLoader()
        loader.suiteClass = CountingTestSuite
        test_suite = loader.loadTestsFromTestCase(test_union)
    else:
        assert issubclass(test_union, CountingTestSuite), f'Expected CountingTestSuite or TestCase, got {test_union}'
        test_suite = test_union
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    if result.testsRun == 0:
        raise f"Test class {test_suite} has no tests."
    errors_count = len(result.failures) + len(result.errors)

    # AdditionTestCase(unittest.TestCase)
    # test_suite = <unittest.suite.TestSuite tests=[None]>
    # test_suite.__class__ = <class 'unittest.suite.TestSuite'>
    # test_suite._tests = [None]

    # TestLispIntepreter(unitai.TestCase)
    # issubclass(test_union, unitai.TestCase) => True
    # test_suite = <unittest.suite.TestSuite tests=[None, None, None, None]>

    # if issubclass(test_union, unitai.TestCase):
    # We can count the assertions instead of just test passed tests

    # if getattr(result, 'passed_assertions', None) is not None:
    try:
        if not test_suite.ai_test_case:
            raise Exception()
        total_passed_assertions = test_suite.total_passed_assertions
        # TODO: qui bisogna leggere passed_assertions dal test_suite, perche' result.passed_assertions e'
        # solo l'ultimo sub-test passato, non il totale
        log('Using unitai.TestCase')
        total_assertions = count_assertions(test_union)
        log(f"Total assertions: {total_assertions}, Passed: {total_passed_assertions}")
        if total_assertions == 0 or total_passed_assertions > total_assertions:
            raise Exception()
        score = total_passed_assertions / total_assertions
    except Exception as exc:
        # log('We recommend your test classes extend unitai.TestCase (instead of unittest.TestCase), for smoother scoring')
        score = 1 - errors_count / result.testsRun
        total_passed_assertions, total_assertions = None, None
    error_strings = []
    for test_suite, error_str in result.errors + result.failures:
        error_strings.append(cleanup_error_str(error_str))
    return error_strings, errors_count, total_passed_assertions, total_assertions, score


def remove_lines_with(lines, is_target):
    try:
        target_line = -1
        for i, line in enumerate(lines):
            if is_target(line):
                target_line = i
                break
        if target_line >= 0:
            # Remove the target line and those before and after:
            lines = lines[:target_line - 1] + lines[target_line + 2:]
        return lines
    except Exception as e:
        traceback.print_exc()
        return lines


def cleanup_error_str(error_str):
    # Remove every reference to the file path:
    error_str = re.sub(r'File ".*", line', 'line', error_str)
    # Find the line with "eval" and "self.func_name":
    lines = error_str.split('\n')

    lines = remove_lines_with(lines, lambda line: 'eval(' in line and '{self.func_name}' in line)
    lines = remove_lines_with(lines, lambda line: 'exec(code)' in line)
    lines = remove_lines_with(lines, lambda line: 'return ___eval(' in line)

    # Put back together the redacted lines
    error_str = '\n'.join(lines)
    return error_str


def parse_ai_output(t: str) -> Dict:
    # find anything between <implements name="..."> and </implement>
    found = re.findall(r'<implement name="(.+?)">(.*?)</implement>', t, re.DOTALL)
    found_dict = dict(found)
    return found_dict


def count_assertions(test_case: TestCase):
    src = inspect.getsource(test_case)
    lines = src.split('\n')
    count = 0
    for line in lines:
        if 'self.assert' in line and not line.strip().startswith('#'):
            count += 1
    return count


def index_of_first_non_empty_char(line: str) -> int:
    for i, c in enumerate(line):
        if c != ' ':
            return i
    return -1


def remove_extra_indentation(code: str):
    lines = code.split('\n')
    for line in lines:
        i = index_of_first_non_empty_char(line)
        if i >= 0:
            break
    ret = []
    for line in lines:
        ret.append(line[i:])
    return '\n'.join(ret)
