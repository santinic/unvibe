import unittest

import unittestai


class TestTestCase(unittest.TestCase):
    """Some inception going on here"""

    def test_wraps_and_count(self):
        tc = unittestai.TestCase()
        tc.assertEqual(1, 1)
        tc.assertTrue(True)
        tc.assertGreater(2, 1)
        try:
            tc.assertEqual(1, 0)
        except Exception:
            pass

        try:
            tc.assertFalse(True)
        except Exception:
            pass
        self.assertEqual(tc.passed_assertions, 3)
