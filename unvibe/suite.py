import unittest

from unittest import TestSuite, TextTestResult


def incr_assertions_counter(test_case, name):
    if hasattr(test_case._outcome.result, name):
        setattr(test_case._outcome.result, name, getattr(test_case._outcome.result, name) + 1)
    else:
        setattr(test_case._outcome.result, name, 1)


class MyTextTestResult(TextTestResult):
    def __init_(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addError(self, test, err):
        print('>> ERROR')
        incr_assertions_counter(test, 'ass_failed')
        incr_assertions_counter(test, 'ass_executed')
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
                method = getattr(self, name)
                setattr(self, name, self._wrap_assert(method))

    def _wrap_assert(self, method):
        def wrapper(*args, **kwargs):
            try:
                method(*args, **kwargs)
                incr_assertions_counter(self, 'ass_executed')
                incr_assertions_counter(self, 'ass_passed')
                # print('\t\t', self._outcome.result.passed_assertions)
            except Exception as e:
                incr_assertions_counter(self, 'ass_executed')
                incr_assertions_counter(self, 'ass_failed')
                raise e

        return wrapper
