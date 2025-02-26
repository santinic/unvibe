# UnitAI: Generate code that passes unit-tests

UnitAI quickly generates many alternative implementations for functions
and classes you annotate with `@ai`, and re-runs your unit-tests until
it finds a correct implementation.

The algorithm tries

This approach has been demonstrated in research and in practice to produce
much better results than simply using code-generation alone
(see [Research Chapter](#research)).

## Example

```python
from unitai import ai

@ai
def validate_email(email: str) -> bool:
    """Validate """
    pass


```

```
$ python -m unitai test_validate_email.py
```

The library will re-run the tests and generate many

## Setup & Configuration

```
$ pip install unitai
```

Write in your project folder a `.unitai.json` config file.

```json 
{
  "ai": {
    "provider": "claude", // or "openai"
    "api_key": "...",
    "params": {
      "model": "claude-3-5-sonnet-20240620", // or "gpt-3.5-turbo"
      "max_tokens": 1000,
      "temperature": 0
    }
  }
}
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

## Citation

```
@article{santini2025,
  title={UnitAI: Generate code that passes unit-tests},
  url={https://claudio.uk/posts/unitai.html}, 
  author={Santini, Claudio},
  year={2025}
}
```
