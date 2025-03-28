import traceback
import unittest

from unvibe import reset
from unvibe.tests_container import ClassTestsContainer
from unvibe.core import start_search


class BaseTest(unittest.TestCase):
    def setUp(self):
        reset()

    def base(self, functions, test_class, **kwargs):
        try:
            test_container = ClassTestsContainer(test_class)
            state = start_search(functions, test_container, **kwargs)
        except Exception as exc:
            traceback.print_exc()
            raise exc
        self.assertEqual(0, len(state.errors))
        self.assertEqual(1.0, state.score)
        self.assertEqual(len(state.mes), len(functions))
        self.assertEqual(set([f.name for f in functions]),
                         set([mf.name for mf in state.mes]))
        return state
