import unittest
from unittest import TestCase

import unvibe
from unvibe.core import run_tests
from unvibe.state import State
from unvibe.suite import MyTextTestResult
from unvibe.tests_container import ClassTestsContainer


class TestCountingTestCase(TestCase):
    def setUp(self):
        class TestClass(unvibe.TestCase):
            def test_success(self):
                self.assertEqual(1, 1)  # ok
                self.assertEqual(2, 2)  # ok

            def test_fail(self):
                self.assertEqual(True, False)  # fail

            def test_error(self):
                self.assertEqual(1, 1)  # ok
                self.assertEqual([][1], 1)  # error
                self.assertEqual(1, 1)  # ok

            def test_error_as_first(self):
                self.assertEqual([][1], 1)  # error

        self.TestClass = TestClass

    def test_counting(self):
        tests_container = ClassTestsContainer(self.TestClass)
        test_suite = tests_container.generate_test_suite()
        runner = unittest.TextTestRunner(resultclass=MyTextTestResult)
        result = runner.run(test_suite)
        self.assertEqual(result.testsRun, 4)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.ass_failed, 3)
        self.assertEqual(result.ass_executed, 6)
        self.assertEqual(result.ass_passed, 3)
        self.assertEqual(tests_container.count_assertions(), 7)

    def test_run_tests(self):
        state = State()
        tests_container = ClassTestsContainer(self.TestClass)
        run_tests(tests_container, state)
        self.assertEqual(state.passed_assertions, 3)
        self.assertEqual(state.failed_assertions, 3)
        self.assertEqual(state.executed_assertions, 6)
        self.assertAlmostEquals(state.score, 0.428, 2)
