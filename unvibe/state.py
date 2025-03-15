from typing import Dict, List

from unvibe import MagicEntity


class State:
    orig_context: str  # all the files at the beginning of the search
    context: str  # the orig_context concatenated with the current implementations from this state
    prompt: str
    ai_output: str
    impls: Dict[str, str]  # For each function, the source-code implementation: func_name -> code implementation.
    mes: List[MagicEntity]  # the magic functions with their original definitions and "current" implementations
    tests: str  # the source code of the test class
    errors: List[str]  # the errors we got from the tests
    score: float  # the score for this solution
    passed_assertions: int
    total_assertions: int
    executed_assertions: int
    failed_assertions: int
    children: List['State']
    temperature: float = None
    count = None

    def __init__(self):
        self.orig_context: str = ''
        self.context: str = None
        self.prompt: str = None
        self.ai_output: str = None
        self.impls: Dict[str, str] = {}
        self.mes: List[MagicEntity] = None
        self.tests: str = None
        self.errors: List[str] = []
        self.score: float = None
        self.passed_assertions: int = 0
        self.total_assertions: int = 0
        self.executed_assertions: int = 0
        self.failed_assertions: int = 0
        self.children: List['State'] = []
        self.temperature: float = None
        self.count = None

    def build_context_from_magic_entities(self):
        context = self.orig_context
        for mf in self.mes:
            context += (mf.impl if mf.impl is not None else mf.clean_orig_code) + '\n'
        return context

    def __repr__(self):
        return f'State(#{self.count}, score={self.score:.2f}, errors={len(self.errors)}, temp={self.temperature:.3f})'

    def to_dict(self):
        return {
            'count': self.count,
            'context': self.context,
            'prompt': self.prompt,
            'ai_output': self.ai_output,
            'impls': self.impls,
            'mfs': [mf.to_dict() for mf in self.mes],
            'tests': self.tests,
            'errors': self.errors,
            'score': self.score,
            'passed_assertions': self.passed_assertions,
            'total_assertions': self.total_assertions,
            'executed_assertions': self.executed_assertions,
            'failed_assertions': self.failed_assertions,
            'temperature': self.temperature,
            'children': [child.to_dict() for child in self.children]
        }
