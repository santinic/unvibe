import argparse
import sys
from datetime import datetime
from pathlib import Path

from unittestai import magic_entities
from unittestai.TestsContainer import FolderPatternTestsContainer
from unittestai.core import start_search
from unittestai.state import State

epilog = '''examples:
  unittestai src/ tests/                    # Uses every file in src/ and tests/ folders
  unittestai src/main.py test/test_main.py  # Use only the indicated files
'''


def main():
    parser = argparse.ArgumentParser(
        description='UnitAI - Generate code that pass unit-tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)
    parser.add_argument('sources', help='source file or sources folder')
    parser.add_argument('tests', help='unit test file or tests folder')
    parser.add_argument('-o', '--output_folder', default='.', help='output folder for new implementations')
    parser.add_argument('-p', '--pattern', default='test*.py', help='pattern for test files')
    if len(sys.argv) <= 2:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    tests_container = FolderPatternTestsContainer(args.tests, args.pattern)
    tests_container.generate_test_suite()
    context = get_context(args)
    best_state = start_search(magic_entities, tests_container, sources)
    write_output_folder(best_state, args.output_folder)


def get_context(args) -> str:
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

    final_text = f'''
    # UnittestAI Execution output.
    {msg}
    # Score: {state.score}
    # Passed assertions: {state.passed_assertions}/{state.total_assertions}
    '''
    if len(state.errors) > 0:
        all_errors = '=====\n'.join(state.errors)
        commented_errors = ''
        for line in all_errors.split('\n'):
            commented_errors += '# ' + line + '\n'
        final_text += commented_errors
    for me in state.mes:
        final_text += f'\n{me.impl}\n'
    time = datetime.now().strftime('%H-%M-%S')
    Path(output_folder).mkdir(exist_ok=True)
    file_path = Path(output_folder) / f'unittestai_output_{time}'
    with open(file_path, 'w') as f:
        f.write(final_text)
    print('Written results to', file_path)


if __name__ == '__main__':
    main()
