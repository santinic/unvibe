import importlib
import inspect
import sys
import unittest
from abc import abstractmethod
from pathlib import Path
from unittest import TestSuite, TestLoader, TestCase

from unittestai.suite import CountingTestSuite


def count_assertions(src: str) -> int:
    lines = src.split('\n')
    count = 0
    for line in lines:
        if 'self.assert' in line and not line.strip().startswith('#'):
            count += 1
    return count

def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestsContainer:
    def __init__(self):
        pass

    @abstractmethod
    def generate_test_suite(self) -> TestSuite:
        pass

    @abstractmethod
    def get_source(self) -> str:
        pass

    @abstractmethod
    def count_assertions(self):
        pass


class ClassTestsContainer(TestsContainer):
    def __init__(self, test_suite: TestSuite):
        self.test_suite = test_suite

    def generate_test_suite(self) -> TestSuite:
        loader = TestLoader()
        loader.suiteClass = CountingTestSuite
        test_suite = loader.loadTestsFromTestCase(self.test_suite)
        return test_suite

    def get_source(self):
        return inspect.getsource(self.test_suite)

    def count_assertions(self):
        src = inspect.getsource(self.test_suite)
        return count_assertions(src)


class FolderPatternTestsContainer(TestsContainer):
    def __init__(self, test_folder, pattern):
        super().__init__()
        self.test_folder = test_folder
        self.pattern = pattern
        self.test_sources = self._get_all_test_sources()

    def _get_all_test_sources(self) -> str:
        tests_path = Path(self.test_folder)
        if tests_path.is_file():
            tests_file_names = [tests_path]
        else:
            tests_file_names = list(tests_path.glob(self.pattern))
            if len(tests_file_names) == 0:
                print('No test files found in', self.test_folder)
                sys.exit(1)
            print(f'{len(tests_file_names)} test files found')
        ctx = '\n'.join([f.read_text() for f in tests_file_names])
        return ctx

    def generate_test_suite(self):
        if Path(self.test_folder).is_file():
            module = import_from_path('module', self.test_folder)
            return unittest.TestLoader().loadTestsFromModule(module)
        else:
            # is a folder
            test_loader = unittest.TestLoader()
            test_loader.suiteClass = CountingTestSuite  # Count the passed assertions if possible
            test_suite: TestSuite = test_loader.discover(self.test_folder, self.pattern)
            print(f'{test_suite.countTestCases()} test cases found')
            return test_suite

    def get_source(self):
        return self.test_sources

    def count_assertions(self):
        return count_assertions(self.test_sources)
