import unittestai
from tests_e2e.disk_cache.disk_cache import disk_cache


class TestDiskCache(unittestai.TestCase):
    def test_annotation(self):
        @disk_cache
        def fibonacci(n: int) -> int:
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(20), 6765)
        self.assertEqual(fibonacci(30), 832040)
