from unitai.TestCase import TestCase as unitai_TestCase

from unitai.magic import MagicFunction
from .ai import ai_call

magic_functions = []
config = None
TestCase = unitai_TestCase


def reset():
    magic_functions.clear()


def ai(thing) -> MagicFunction:
    """The @ai annotation used on functions and classes"""
    mf = MagicFunction(thing)  # TODO: Implement also for classes
    print(f'[UnitAI] Adding {mf} to magic functions')
    magic_functions.append(mf)
    return mf
