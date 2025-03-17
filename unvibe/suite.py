import unittest
from collections import defaultdict

from unittest import TestSuite, TextTestResult, TestResult


def jet(obj, keys):
    keys = keys.split('.')
    try:
        x = getattr(obj, keys[0])
        for key in keys[1:]:
            x = getattr(x, key)
        return x
    except AttributeError:
        return None

class UnvibeTestResult(TestResult):
    ass_passed: int
    ass_executed: int
    ass_failed: int

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.failed_tests = defaultdict(lambda: 0)
        self.ass_passed = 0
        self.ass_executed = 0
        self.ass_failed = 0

    def addError(self, test, err):
        method_name = test._testMethodName
        self.failed_tests[method_name] += 1
        self.ass_failed += 1
        self.ass_executed += 1
        super().addError(test, err)


class CountingTestSuite(TestSuite):
    """A unittest.TestSuite that counts the number of successful assertions."""

    def __init__(self, tests=()):
        self.ai_test_case = False
        self.ass = dict()
        super().__init__(tests)

    def _tearDownPreviousClass(self, test, result):
        if hasattr(result, 'ass_executed'):
            self.ai_test_case = True
        super()._tearDownPreviousClass(test, result)


class TestCase(unittest.TestCase):
    """
    Wraps all assertEqual, assertTrue etc. methods from unittest.TestCase,
    but counting the successful ones in a global counter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in dir(self):
            if name.startswith('assert'):
                assert_method = getattr(self, name)
                setattr(self, name, self._wrap_assert(assert_method))

    # def print_status(self, when, method):
    #     method_name = jet(self, '_testMethodName')
    #     tuple = (
    #         jet(self, '_outcome.result.ass_passed'),
    #         jet(self, '_outcome.result.ass_executed'),
    #         jet(self, '_outcome.result.ass_failed')
    #     )
    #     print(when, '\t\t', method_name, '\t\t', tuple)

    def _wrap_assert(self, assert_method):
        def wrapper(*args, **kwargs):
            # self.print_status('before', assert_method)
            try:
                assert_method(*args, **kwargs)
                self._outcome.result.ass_executed += 1
                self._outcome.result.ass_passed += 1
                # self.print_status('after', assert_method)
            except Exception as e:
                self._outcome.result.ass_executed += 1
                self._outcome.result.ass_failed += 1
                # self.print_status('after exc', assert_method)
                raise e

        return wrapper

    # def __setattr__(self, name, value):
    #     """standard implementation for setattr:"""
    #     print('SETATTR', name, value)
    #     self.__dict__[name] = value

