import unvibe
from tests_e2e.sqrt.src.sqrt import my_sqrt


class SqrtTest(unvibe.TestCase):
    def test_sqrt_integer(self):
        self.assertEqual(type(my_sqrt(4)), float)
        self.assertAlmostEquals(my_sqrt(4), 2, 2)
        self.assertAlmostEquals(my_sqrt(16), 4, 2)
        self.assertAlmostEquals(my_sqrt(25), 5, 2)
        self.assertAlmostEquals(my_sqrt(36), 6, 2)

    def test_sqrt_float(self):
        self.assertAlmostEquals(my_sqrt(4.0), 2.0, 2)
        self.assertAlmostEquals(my_sqrt(16.0), 4.0, 2)
        self.assertAlmostEquals(my_sqrt(25.0), 5.0, 2)
        self.assertAlmostEquals(my_sqrt(36.0), 6.0, 2)

    def test_sqrt_zero(self):
        self.assertAlmostEquals(my_sqrt(0), 0, 2)
        self.assertAlmostEquals(my_sqrt(0.0), 0.0, 2)

    def test_sqrt_negative(self):
        self.assertAlmostEquals(my_sqrt(-4), 2, 2)
        self.assertAlmostEquals(my_sqrt(-16), 4, 2)
        self.assertAlmostEquals(my_sqrt(-25), 5, 2)
        self.assertAlmostEquals(my_sqrt(-36), 6, 2)
