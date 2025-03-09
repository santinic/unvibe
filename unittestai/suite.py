import unittest

from unittest import TestSuite


class CountingTestSuite(TestSuite):
    """A unittest.TestSuite that counts the number of successful assertions."""

    def __init__(self, tests=()):
        self.total_passed_assertions = 0
        self.ai_test_case = False
        super().__init__(tests)

    def _tearDownPreviousClass(self, test, result):
        if getattr(result, 'passed_assertions', None) is not None:
            self.ai_test_case = True
            self.total_passed_assertions += result.passed_assertions
        super()._tearDownPreviousClass(test, result)


class TestCase(unittest.TestCase):
    """
    Wraps all assertEqual, assertTrue etc. methods from unittest.TestCase,
    but counting the successful ones in a global counter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_assertions = 0
        for name in dir(self):
            if name.startswith('assert'):
                method = getattr(self, name)
                setattr(self, name, self._wrap_assert(method))

    def _wrap_assert(self, method):
        def wrapper(*args, **kwargs):
            try:
                method(*args, **kwargs)
            except AssertionError as e:
                raise e
            else:
                self.passed_assertions += 1

        return wrapper

    def tearDown(self):
        # In the end, save into the TestResult the number of passed assertions
        self._outcome.result.passed_assertions = self.passed_assertions
        super().tearDown()
