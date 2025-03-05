import unittest


class SqrtTest(unittest.TestCase):
    def test_sqrt_integer(self):
        self.assertEqual(sqrt(4), 2)
        self.assertEqual(sqrt(16), 4)
        self.assertEqual(sqrt(25), 5)
        self.assertEqual(sqrt(36), 6)

    def test_sqrt_float(self):
        self.assertEqual(sqrt(4.0), 2.0)
        self.assertEqual(sqrt(16.0), 4.0)
        self.assertEqual(sqrt(25.0), 5.0)
        self.assertEqual(sqrt(36.0), 6.0)

    def test_sqrt_zero(self):
        self.assertEqual(sqrt(0), 0)
        self.assertEqual(sqrt(0.0), 0.0)

    def test_sqrt_negative(self):
        self.assertEqual(sqrt(-4), 2)
        self.assertEqual(sqrt(-16), 4)
        self.assertEqual(sqrt(-25), 5)
        self.assertEqual(sqrt(-36), 6)
