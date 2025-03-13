import unittest

import unvibe
from tests_e2e.disk_cache.disk_cache import disk_cache, get_keys


class TestDiskCache(unvibe.TestCase):
    def test_annotation(self):
        @disk_cache
        def fibonacci(n: int) -> int:
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        self.assertEqual(get_keys(), [])
        self.assertEqual(fibonacci(1), 1)
        self.assertEqual(get_keys(), {'fibonacci_1'})
        self.assertEqual(fibonacci(2), 2)
        self.assertEqual(get_keys(), {'fibonacci_1', 'fibonacci_2'})
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(20), 6765)
        self.assertEqual(fibonacci(30), 832040)

    @unittest.skip("")
    def test_another(self):
        @disk_cache
        def sum_n(n: int) -> int:
            return sum_n(n - 1) + n if n > 0 else 0

        self.assertEqual(sum_n(10), 55)
        self.assertEqual(sum_n(100), 5050)
