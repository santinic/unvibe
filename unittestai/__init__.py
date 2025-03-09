from typing import List, Union

from unittestai.suite import TestCase as MyTestCase

from unittestai.magic import MagicFunction, MagicEntity, MagicClass
from .ai import ai_call
from .log import log

magic_entities: List[MagicEntity] = []
config = None
TestCase = MyTestCase


def reset():
    magic_entities.clear()


def ai(thing: Union[type, callable]) -> Union[MagicFunction, type]:
    """The @ai annotation used on functions and classes"""
    if isinstance(thing, type):
        mc = MagicClass(thing)
        log(f'Adding {mc} to magic classes')
        magic_entities.append(mc)
        return mc
    elif callable(thing):
        mf = MagicFunction(thing)
        magic_entities.append(mf)
        log(f'Adding {mf} to magic functions')
        return mf
    else:
        raise ValueError(f'@ai expected a class or a function, got {thing}')

