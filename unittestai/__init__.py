from unittestai.suite import TestCase as MyTestCase

from unittestai.magic import MagicFunction
from .ai import ai_call

magic_functions = []
config = None
TestCase = MyTestCase


def reset():
    magic_functions.clear()


def ai(thing) -> MagicFunction:
    """The @ai annotation used on functions and classes"""
    mf = MagicFunction(thing)  # TODO: Implement also for classes
    print(f'[UnitAI] Adding {mf} to magic functions')
    magic_functions.append(mf)
    return mf
