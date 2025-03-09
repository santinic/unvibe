import argparse
import sys
import unittest
from unittest import TestSuite

from unittestai import magic_entities
from unittestai.core import start_search
from unittestai.suite import CountingTestSuite

epilog = '''examples:
  unitai src/ tests/                    # Uses every file in src/ and tests/ folders
  unitai src/main.py test/test_main.py  # Use only the indicated files
'''


def main():
    parser = argparse.ArgumentParser(
        description='UnitAI - Generate code that pass unit-tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)
    # parser.add_argument('source', help='source file or folder')
    parser.add_argument('tests', help='unit test file or folder')
    parser.add_argument('-r', '--replace', action='store_true', help='replace original files with new implementations')
    parser.add_argument('-o', '--output', help='output folder for new implementations')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    # args_for_unittest_main = sys.argv
    # print(args_for_unittest_main)
    # TestProgram(module=None, argv=args_for_unittest_main)

    # Use Unittest library to find all the test classes in the given folder:
    test_loader = unittest.TestLoader()
    test_loader.suiteClass = CountingTestSuite  # Count the passed assertions if possible
    test_suite: TestSuite = test_loader.discover(args.tests)
    print(f'{test_suite.countTestCases()} test cases found')
    start_search(magic_entities, test_suite)


if __name__ == '__main__':
    main()
