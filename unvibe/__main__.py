import argparse
import sys
import time
from pathlib import Path

from unvibe import magic_entities, log, project_name
from unvibe.state import State

epilog = f'''examples:
  {project_name} src/ tests/                    # Uses every file in src/ and tests/ folders
  {project_name} src/main.py test/test_main.py  # Use only the indicated files
'''


def parse_args_and_run_main() -> State:
    parser = argparse.ArgumentParser(
        description='Unvibe - Generate code that pass unit-tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)
    parser.add_argument('sources', help='sources folder')
    parser.add_argument('tests', help='unit-tests folder')
    parser.add_argument('-o', '--output_folder', default='.', help='output folder for new implementations')
    parser.add_argument('-p', '--pattern', default='test*.py', help='pattern for test files')
    parser.add_argument('-d', '--display_report', help='Display HTML report for the search tree', action='store_true', default=False)
    if len(sys.argv) <= 2:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()

    return main(args)


def main(args) -> (State, str):
    from unvibe.tests_container import FolderPatternTestsContainer
    from unvibe.core import start_search
    log('Sources:', args.sources)
    log('Tests:', args.tests)
    tests_container = FolderPatternTestsContainer(args.tests, args.pattern)
    tests_container.generate_test_suite()
    sources = get_sources_context(args)
    best_state = start_search(magic_entities, tests_container, sources, args.display_report)
    output_file = write_output_folder(best_state, args.output_folder)
    return best_state, output_file


def get_sources_context(args) -> str:
    sources = Path(args.sources)
    if sources.is_file():
        return sources.read_text()
    elif sources.is_dir():
        context = ''
        for file in sources.glob('*.py'):
            context += file.read_text() + '\n'
        return context
    else:
        raise FileNotFoundError(f'File or folder not found: {args.sources}')


def write_output_folder(state: State, output_folder):
    if state.score == 1:
        msg = '# This implementation passed all tests'
    elif state.score == 0:
        msg = ('# Could not find any implementation that passes any test. Check the errors returned from the tests'
               '# You may want to try a different model, change max_temperature, max_depth or random_spread params.')
    else:
        msg = '# This is the best implementation we found, but it did not pass all the tests. Check the errors below.'

    test_case_msg = f'(make your test classes extend {project_name}.TestCase to see this)' if state.passed_assertions is None else ''
    final_text = f'''# {project_name.capitalize()} Execution output.
{msg}
# Score: {state.score}
# Passed assertions: {state.passed_assertions}/{state.total_assertions} {test_case_msg}
'''
    if state.score < 1:
        all_errors = '=====\n'.join(state.errors)
        commented_errors = ''
        for line in all_errors.split('\n'):
            commented_errors += '# ' + line + '\n'
        final_text += commented_errors
    for key, impl in state.impls.items():
        final_text += f'\n{impl}\n'
    timestamp = int(time.time())
    Path(output_folder).mkdir(exist_ok=True)
    me_names = '_'.join([me.name for me in state.mes])
    file_path = Path(output_folder) / f'{project_name}_{me_names}_{timestamp}.py'
    with open(file_path, 'w') as f:
        f.write(final_text)
    print('Written results to', file_path)
    return file_path


if __name__ == '__main__':
    parse_args_and_run_main()
