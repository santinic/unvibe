from typing import List, Union

from unvibe.suite import TestCase as MyTestCase

from unvibe.magic import MagicFunction, MagicEntity, MagicClass
from unvibe.log import log

project_name = 'unvibe'
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

