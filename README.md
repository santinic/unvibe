# Unvibe: Generate code that passes unit-tests
[![Installing via pip and running](https://github.com/santinic/unvibe/actions/workflows/pip-install.yml/badge.svg)](https://github.com/santinic/unvibe/actions/workflows/pip-install.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unvibe)
![PyPI - Version](https://img.shields.io/pypi/v/unvibe)

Unvibe quickly generates many alternative implementations for functions
and classes you annotate with `@ai`, and re-runs your unit-tests until
it finds a correct implementation.

This approach has been demonstrated in research and in practice to produce
much better results than simply using code-generation alone
(see [Research Chapter](#research)).

It's particularly effective on large projects with decent test coverage.

It works with most AI providers: local Ollama, OpenAI, DeepSeek, Claude, Gemini,

## Install

Just add `unvibe` as a dependency to your project:

`pip install unvibe`

## Example

First define a new function in your existing Python project. Then annotate it with `@ai`:
Let's implement a Lisp interpreter in Python with Unvibe. We start with creating a `lisp.py`:

```python
from unvibe import ai


@ai
def lisp(expr: str) -> bool:
    """A simple lisp interpreter compatible with Python lists and functions"""
    pass
```

Now, let's write a few unit-tests, to define how the function should behave. 
In `test_list.py`:

```python
import unvibe
from lisp import lisp


# You can also inherit unittest.TestCase, but unvibe.TestCase provides a better reward function
class LispInterpreterTestClass(unvibe.TestCase):
    def test_calculator(self):
        self.assertEqual(lisp("(+ 1 2)"), 3)
        self.assertEqual(lisp("(* 2 3)"), 6)

    def test_nested(self):
        self.assertEqual(lisp("(* 2 (+ 1 2))"), 6)
        self.assertEqual(lisp("(* (+ 1 2) (+ 3 4))"), 21)

    def test_list(self):
        self.assertEqual(lisp("(list 1 2 3)"), [1, 2, 3])

    def test_call_python_functions(self):
        self.assertEqual(lisp("(list (range 3)"), [0, 1, 2])
        self.assertEqual(lisp("(sum (list 1 2 3)"), 6)
```

Now, we can use UnitAI to search for a valid implementation that passes all the tests:

```
$ python -m unvibe lisp.py test_lisp.py
```

The library will re-run the tests and generate many alternatives, and keep exploring the ones that pass
more tests, while feeding back the test errors to the LLM. In the end you will find a new file
called `unvibe_lisp.py` with a valid implementation:

```python
# Unvibe Execution output.
# This implementation passed all tests
# Score: 1.0
# Passed assertions: 7/7 


def lisp(exp):
    def tokenize(exp):
        return exp.replace('(', ' ( ').replace(')', ' ) ').split()

    def parse(tokens):
        if len(tokens) == 0:
            raise SyntaxError('Unexpected EOF')
        token = tokens.pop(0)
        if token == '(':
            L = []
            while tokens[0] != ')':
                L.append(parse(tokens))
            tokens.pop(0)  # Remove ')'
            return L
        elif token == ')':
            raise SyntaxError('Unexpected )')
        else:
            try:
                return int(token)
            except ValueError:
                return token

    def evaluate(x):
        if isinstance(x, list):
            op = x[0]
            args = x[1:]
            if op == '+':
                return sum(evaluate(arg) for arg in args)
            elif op == '*':
                result = 1
                for arg in args:
                    result *= evaluate(arg)
                return result
            elif op == 'list':
                return [evaluate(arg) for arg in args]
            else:
                # Call Python functions
                return globals()[op](*[evaluate(arg) for arg in args])
        return x

    tokens = tokenize(exp)
    return evaluate(parse(tokens))
```




## Setup & Configuration

```
$ pip install unvibe
```

Write in your project folder a `.unvibe.toml` config file.

```toml 
# For example, to use Claude:
[ai]
provider = "claude"
api_key = "sk-..."
model = "claude-3-5-haiku-latest"
max_tokens = 5000

# Or, to use a local Ollama:
[ai]
provider = "ollama"
model = "deepseek-r1:8b"
host = "http://localhost:11434"

# To use OpenAI or DeepSeek API:
[ai]
provider = "openai"
base_url = "https://api.deepseek.com"
api_key = "sk-..."
temperature = 0.0
max_tokens = 1024

# To Use Gemini API:
[ai]
provider = "gemini"
api_key = "..."
model = "gemini-2.0-flash"

# Advanced Parameters to tune the search: 
[search]
random_spread = 4       # How many random tries to make before selecting the best move.
max_depth = 8           # Maximum depth of the search tree.
max_temperature = 0.3   # Picks random temperatures up to this value.
# Some models perform better at lower temps, in general
# Higher temperature = more exploration
```

## Research

This approach has been explored in various research papers. For example, from
"LLM-based Test-driven Interactive Code Generation: User Study and Empirical Evaluation"
(Microsoft Research) https://arxiv.org/abs/2404.10100v1:
> Our results are promising with using the OpenAI Codex LLM on MBPP: our best algorithm
> improves the pass@1 code generation accuracy metric from 48.39% to 70.49% with a single
> user query, and up to 85.48% with up to 5 user queries. Second, we can generate a
> non-trivial functional unit test consistent with the user intent within an average
> of 1.69 user queries for 90.40% of the examples for this dataset.

## Related Article

For more information, check the original article: [Unvibe: Generate code that passes unit-tests](https://claudio.uk/posts/unvibe.html)
