import unittest

from unittest import TestSuite


class CountingTestSuite(TestSuite):
    """A unittest.TestSuite that counts the number of successful assertions."""

    def __init__(self, tests=()):
        self.total_passed_assertions = 0
        self.total_executed_assertions = 0
        self.total_failed_assertions = 0
        self.ai_test_case = False
        super().__init__(tests)

    def _tearDownPreviousClass(self, test, result):
        if hasattr(result, 'passed_assertions'):
            self.ai_test_case = True
            if hasattr(result, 'passed_assertions'):
                self.total_passed_assertions = result.passed_assertions
            if hasattr(result, 'executed_assertions'):
                self.total_executed_assertions = result.executed_assertions
            if hasattr(result, 'failed_assertions'):
                self.total_failed_assertions = result.failed_assertions
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
                method = getattr(self, name)
                setattr(self, name, self._wrap_assert(method))

    def incr_assertions_counter(self, name):
        if hasattr(self._outcome.result, name):
            setattr(self._outcome.result, name, getattr(self._outcome.result, name) + 1)
        else:
            setattr(self._outcome.result, name, 1)

    def _wrap_assert(self, method):
        def wrapper(*args, **kwargs):
            self.incr_assertions_counter('executed_assertions')
            # with self.subTest():
            print(*args, **kwargs)
            try:
                method(*args, **kwargs)
                print('pass')
                self.incr_assertions_counter('passed_assertions')
                print('\t\t', self._outcome.result.passed_assertions)
            except AssertionError as e:
                print('fail', e)
                self.incr_assertions_counter('failed_assertions')
                raise e

        return wrapper
