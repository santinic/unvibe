import re
import traceback
import unittest
from copy import copy
from pprint import pprint
from random import random
from typing import List, Dict

from unvibe import magic_entities
from unvibe.llm import ai_call
from unvibe.suite import MyTextTestResult
from unvibe.tests_container import TestsContainer
from unvibe.config import config, config_get_or
from unvibe.log import log
from unvibe.magic import cleanup_implementation, MagicEntity
from unvibe.rand import up_to_1
from unvibe.state import State
from unvibe.ui import create_page_and_open_browser


def generate_new_state(count, state: State, temperature: float, tests_container: TestsContainer) -> State:
    """Generates a new state for program space search"""
    new_state = State()
    new_state.mes = state.mes
    new_state.count = count
    new_state.tests = state.tests
    new_state.temperature = temperature
    first_error = [state.errors[0]] if len(state.errors) > 0 else []
    prompt, resp_text = ai_call(state.mes, state.context, state.tests, first_error, temperature)
    new_state.prompt = prompt
    new_state.ai_output = resp_text
    impls = parse_ai_output(resp_text)
    new_state.impls = impls
    pprint(impls)
    # If returned implementations is subset of expected implementations:
    has_all_impls = {me.name for me in state.mes} <= set(impls.keys())

    if has_all_impls:
        log(f'Received {len(impls)} implementations, expected {len(state.mes)}')
        for me in new_state.mes:
            if me.name in impls:
                cleaned_up = cleanup_implementation(impls[me.name], me.__class__)
                me.set_impl(cleaned_up)
            else:
                raise Exception(f'Expected implementation for {me.name}')
        new_state.context = new_state.build_context_from_magic_entities()
        run_tests(tests_container, new_state)
        # Reset implementations:
        for me in new_state.mes:
            me.set_impl(None)
    else:
        log('LLM OUTPUT:', resp_text)
        new_state.score = 0
        expected_func_names = ', '.join([me.name for me in new_state.mes])
        new_state.errors = [f'Expected implementations for {expected_func_names}.\n'
                            f'Did you use one <implement> for each function? Try again.']
        log(new_state.errors)
    return new_state


def start_search(mes: List[MagicEntity], tests_container: TestsContainer, sources='', display_tree=False):
    log('Using model', config['ai']['model'])

    # Check all magic entities are registered
    for me in mes:
        assert me in magic_entities, f'{me} not registered with @ai'

    # Run the tree search
    root, states = search(mes, tests_container, sources, display_tree)
    best_state = states[0]
    if display_tree:
        file = create_page_and_open_browser(root)
        print(f'Created execution report {file}')
    return best_state


def get_temperatures(depth):
    random_spread = config_get_or('search', 'random_spread', 2)
    if depth == 0:
        random_spread = config_get_or('search', 'initial_spread', 10)
    random_type = config_get_or('search', 'random_type', 'uniform')
    max_temperature = config_get_or('search', 'max_temperature', 0.7)

    # Generate a bunch of rand temperatures, but always try temp=0
    if random_type == 'increasing':
        return [up_to_1.pop(0) for _ in range(random_spread)]
    elif random_type == 'uniform':
        return [0] + [random() * max_temperature for _ in range(random_spread)]
    else:
        raise Exception(f'Unknown random_type "{random_type}". Use either "increasing" or "uniform"')


def build_initial_context(mes, sources):
    if len(sources) > 0:
        # We have a list of source files, so we replace each MagicEntity with its implementation
        new_context = copy(sources)
        for me in mes:
            if me.impl is None:
                continue
            idx = sources.find(me.orig_code)
            if idx < 0:
                log(f'Could not find {me.orig_code} in context')
                continue
            else:
                new_context = new_context.replace(me.orig_code, me.impl)
        return new_context
    else:
        # We don't have files, just MEs, so we concatenate the implementations
        new_context = ''
        for me in mes:
            new_context += me.orig_code + '\n'
        return new_context


def search(mes: List[MagicEntity], test_container: TestsContainer, sources='', display_tree=False):
    take_best_n = config_get_or('search', 'take_best_n', 3)
    max_depth = config_get_or('search', 'max_depth', 10)

    # Generate the root state
    root = State()
    root.count = 0
    root.mes = mes
    root.temperature = 0.0
    root.tests = test_container.get_source()
    assert type(root.tests) == str
    root.errors = []
    root.score = -1  # root state has no score
    root.context = build_initial_context(mes, sources)
    root.orig_context = root.context
    states = [root]

    found = False
    count = 0
    for depth in range(max_depth):
        log('Depth', depth)
        new_states = []
        # For each state, generate a bunch of new states feeding back the current test errors
        for state in states:
            # Generate a bunch of new states: generate code with LLMs and run the tests to get the score
            for temp in get_temperatures(depth):
                log('Temperature', temp)
                count += 1
                new_state = generate_new_state(count, state, temp, test_container)
                if new_state is None:
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
        if display_tree:
            create_page_and_open_browser(root)
        if found: break
    return root, states


def run_tests(tests_container: TestsContainer, new_state: State):
    """Runs the tests and saves the score/assertions info/errors in the new_state"""
    test_suite = tests_container.generate_test_suite()
    runner = unittest.TextTestRunner(resultclass=MyTextTestResult)
    result = runner.run(test_suite)
    if result.testsRun == 0:
        raise Exception(f"Test class {test_suite} has no tests.")
    errors_count = len(result.failures) + len(result.errors)
    try:
        if not test_suite.ai_test_case:
            raise Exception('Not using unvibe.TestCase')
        log('Using unvibe.TestCase')
        tot_executed = result.ass_executed
        tot_passed = result.ass_passed if hasattr(result, 'ass_passed') else 0
        tot_failed = result.ass_failed if hasattr(result, 'ass_failed') else 0
        total_assertions = tests_container.count_assertions()
        log(f"Total assertions: {total_assertions}, Passed: {tot_passed}, "
            f"Executed: {tot_executed}, Failed: {tot_failed}")
        if total_assertions == 0 or tot_passed > total_assertions:
            raise Exception('Invalid assertions count')
        score = tot_passed / total_assertions
    except Exception as exc:
        log(exc)
        score = 1 - errors_count / result.testsRun
        tot_passed, tot_executed, total_assertions, tot_failed = None, None, None, None
    error_strings = []
    for test_suite, error_str in result.errors + result.failures:
        error_strings.append(cleanup_error_str(error_str))
    new_state.passed_assertions = tot_passed
    new_state.executed_assertions = tot_executed
    new_state.failed_assertions = tot_failed
    new_state.total_assertions = total_assertions
    new_state.errors = error_strings
    new_state.score = score


def remove_lines_with(lines, is_target, minus=1, plus=2):
    try:
        target_line = -1
        for i, line in enumerate(lines):
            if is_target(line):
                target_line = i
                break
        if target_line >= 0:
            # Remove the target line and those before and after:
            lines = lines[:target_line - minus] + lines[target_line + plus:]
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
    lines = remove_lines_with(lines, lambda line: 'line ' in line and 'in wrapper' in line, minus=0, plus=2)
    lines = remove_lines_with(lines, lambda line: 'line ' in line and 'in wrapper' in line, minus=0, plus=2)

    # Put back together the redacted lines
    error_str = '\n'.join(lines)
    return error_str


def parse_ai_output(t: str) -> Dict:
    # find anything between <implements name="..."> and </implement>
    found = re.findall(r'<implement name="(.+?)">(.*?)</implement>', t, re.DOTALL)
    found_dict = dict(found)
    return found_dict


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
