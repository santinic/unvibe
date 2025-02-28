import re
from pprint import pprint
from typing import List, Dict, Tuple

import ollama
import redis
import anthropic
from termcolor import colored
from openai import OpenAI
from google import genai

from . import MagicFunction
from .config import config

redis_client = redis.Redis(host=config['cache']['host'], port=config['cache']['port'], db=config['cache']['db'])
redis_client.ping()


def redis_cached(func):
    """redis memoization for functions"""

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # bypass
        key = f'{func.__name__}__{args}__{kwargs}'
        if redis_client.exists(key):
            print('Return from cache', key[:150] + '…')
            bytes = redis_client.get(key)
            result = bytes.decode('utf-8')
        else:
            result = func(*args, **kwargs)
            redis_client.set(key, result)
            redis_client.expire(key, config['cache']['expire'])
        return result

    return wrapper


@redis_cached
def call_gemini(system, prompt, temperature):
    client = genai.Client(api_key=config['ai']['api_key'])
    resp = client.models.generate_content(
        model=config['ai']['model'],
        contents=system + '\n' + prompt,
    )
    return resp['content']


@redis_cached
def call_openai(system, prompt, temperature):
    # TODO: plugin temperature
    client = OpenAI(api_key=config['ai']['api_key'], base_url=config['ai']['base_url'])
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=config['ai']['max_tokens'],
        # From deepseek.com:
        # USE CASE                  TEMPERATURE
        # Coding / Math:	                0.0
        # Data Cleaning / Data Analysis:    1.0
        # General Conversation:	            1.3
        # Translation:                      1.3
        # Creative Writing / Poetry:        1.5
        temperature=temperature,
        stream=False
    )
    # print('llm resp.choices[0].message.content:', resp.choices[0].message.content)
    return resp.choices[0].message.content


@redis_cached
def call_claude(system, prompt, temperature):
    client = anthropic.Anthropic(api_key=config['ai']['api_key'])
    message = client.messages.create(
        model=config['ai']['model'],
        max_tokens=1000,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    )
    # print('llm output:', message.content)
    return message.content[0].text


@redis_cached
def call_ollama(system, prompt, temperature, model):
    client = ollama.Client(host=config['ai']['host'])
    resp = client.generate(
        model=model,
        prompt=system + '\n' + prompt,
        options=dict(temperature=temperature))
    return resp.response


example = '''
<input>
def pluck(l, key):
    """Pluck a key from a list of dictionaries."""
    pass
    
assert pluck([{'name': 'Alice'}, {'name': 'Bob'}], 'name') == ['Alice', 'Bob']
</input>
<implement name="pluck">
def pluck(l, key):
    return [d[key] for d in l]
</implement>

<input>
def permutations_str(s: str):
    """Return all permutations of a string."""
    pass

class TestPermutations(unittest.TestCase):
    def test_permutations(self):
        self.assertEqual(set(permutations_str('abc')), {'abc', 'acb', 'bac', 'bca', 'cab', 'cba'})
</input>
<implement name="permutations_str">
def permutations_str(s: str):
    from itertools import permutations
    return set(''.join(p) for p in permutations(s))
</implement>

<input>

class Utils:
        def is_palindrome(s: str):
            return s == s[::-2]
    
class TestIsPalindrome(unittest.TestCase):
    def test_is_palindrome(self):
        utils = Utils()
        self.assertTrue(utils.is_palindrome('racecar'))
        self.assertFalse(utils.is_palindrome('hello'))
</input>
<errors>
Traceback (most recent call last):
    line 19, in test_is_palindrome
        self.assertTrue(utils.is_palindrome('racecar'))
</errors>

<implement name="is_palindrome">
        def is_palindrome(s: str):
            return s == s[:-1]
</implement>
'''

system = ("- You only write code inside the <implement> tags.\n"
          "- No explanations before or after.\n"
          "- Only implement the requested functions.\n"
          "- If Errors are provided, fix those errors.\n"
          "- Use as many <implement> as needed. Every function should be in it own <implement> tag.\n")

def ai_call(mfs: List[MagicFunction], context, tests, errors, temperature) -> Tuple[str, Dict[str, str]]:
    assert context.strip() != '', 'Context should not be empty'
    func_names_str = ' '.join([mf.func_name for mf in mfs])
    errors_tag = ''
    if len(errors) > 0:
        errors_tag = '<errors>\n' + '\n'.join(errors) + '</errors>'
    prompt = f'''
{example}
<input>
{context}
</input>
{errors_tag}

Implement the functions: {func_names_str}
'''
    print('LLM PROMPT:', system + '\n' + prompt)
    provider = config['ai']['provider']
    if provider == 'claude':
        resp_text = call_claude(system, prompt, temperature)
    elif provider == 'openai':
        resp_text = call_openai(system, prompt, temperature)
    elif provider == 'gemini':
        resp_text = call_gemini(system, prompt, temperature)
    elif provider == 'ollama':
        resp_text = call_ollama(system, prompt, temperature, model=config['ai']['model'])
    else:
        raise NotImplementedError(f'{provider} not implemented')

    implements_dict = parse_output(resp_text)
    return resp_text, implements_dict


def parse_output(t):
    # find anything between <implements name="..."> and </implement>
    found = re.findall(r'<implement name="(.+?)">(.*?)</implement>', t, re.DOTALL)
    found_dict = dict(found)
    pprint(found_dict)
    return found_dict
