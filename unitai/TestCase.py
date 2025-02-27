import unittest


class TestCase(unittest.TestCase):
    """
    Wraps all assertEqual, assertTrue etc. methods from unittest.TestCase,
    but counting the successful ones in a global counter
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._successes = 0

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
                self._successes += 1

        return wrapper
