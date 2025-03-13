import os
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase

import unvibe
from unvibe.__main__ import main

base_folder = "./tests_e2e"


class TestEndToEnd(TestCase):
    """This test class will be dynamically populated with test cases in tests_e2e/"""
    pass


def create_base_test(folder_name):
    def wrapper(self):
        sources = f"{base_folder}/{folder_name}/src"
        tests = f"{base_folder}/{folder_name}/tests"

        if not Path(sources).exists():
            sources = f"{base_folder}/{folder_name}/{folder_name}.py"
            tests = f"{base_folder}/{folder_name}/test_{folder_name}.py"

        args = SimpleNamespace(
            sources=sources,
            tests=tests,
            pattern='test*.py',  # default unittest pattern
            output_folder='.',  # default output folder
            display_report=False
        )

        print(args)
        unvibe.reset()
        state, output_file = main(args)
        self.assertIsNotNone(state)
        self.assertEqual(state.score, 1)
        self.assertEqual(len(state.errors), 0)
        if state.passed_assertions is not None:
            self.assertGreater(state.passed_assertions, 0)
            self.assertGreater(state.executed_assertions, 0)
            self.assertEqual(state.failed_assertions, 0)

        # Check outputfile exists
        self.assertTrue(Path(output_file).exists())

        # Check it contains a score:
        output_text = Path(output_file).read_text()
        self.assertTrue("Score:" in output_text)

        # Every magic entity should be defined:
        for me in state.mes:
            self.assertIn(me.name, output_text)

    return wrapper


# For every folder inside ../test_e2e, create a test_case
for file in os.listdir(base_folder):
    if (Path(base_folder) / file).is_dir():
        if file.startswith('skip'):
            continue
        folder_name = file
        setattr(TestEndToEnd, f"test_{folder_name}", create_base_test(folder_name))
