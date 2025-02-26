import argparse
import sys

epilog = '''examples:
  unitai src/ tests/                    # Uses every file in src/ and tests/ folders
  unitai src/main.py test/test_main.py  # Use only the indicated files
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='UnitAI - Generate code that pass unit-tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)
    parser.add_argument('source', help='source file or folder')
    parser.add_argument('unit-test', help='unit test file or folder')
    parser.add_argument('-r', '--replace', action='store_true', help='replace original files with new implementations')
    parser.add_argument('-o', '--output', help='output folder for new implementations')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
