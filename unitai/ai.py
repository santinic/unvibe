import re
from pprint import pprint
from typing import List

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
        key = f'{func.__name__}__{args}__{kwargs}'
        if redis_client.exists(key):
            print('Return from cache', key[:150] + '…')
            bytes = redis_client.get(key)
            result = bytes.decode('utf-8')
        else:
            result = func(*args, **kwargs)
            redis_client.set(key, result)
            redis_client.expire(key, config['cache']['expire'])
        print(colored('LLM OUTPUT: ' + result, 'blue'))
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


example = '''Example:
<input>
@ai
def mul(a, b):
    pass
            
def maths():
    def add(a, b):
        return a + b 
       
    @ai 
    def div(a, b):
        pass

    assert mul(2, 3) == 6
    assert div(6, add(2, 1)) == 2
</input>
<errors>
</errors>
<output implement="mul div">
<implement name="mul">
def mul(a, b):
    return a * b
</implement>
<implement name="div">
def div(a, b):
    return a / b
</implement>
</output>

'''


def ai_call(mfs: List[MagicFunction], context, errors, temperature):
    system = ("You only output code inside the <output> tag. No explanations before or after <output>. "
              "Only implement the requested functions. "
              "If <errors> tag is present, fix those errors.")
    errors_str = '\n'.join(errors)
    func_names_str = ' '.join([mf.func_name for mf in mfs])
    assert context.strip() != '', 'Context should not be empty'
    prompt = f'''
{example}
<input>
{context}
</input>
<errors>
{errors_str}
</errors>
<output implement="{func_names_str}">
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
        raise NotImplementedError(f'{config.ai} not implemented')

    implements_dict = parse_output(resp_text)
    return implements_dict


def parse_output(t):
    # find anything between <implements name="..."> and </implement>
    found = re.findall(r'<implement name="(.+?)">(.*?)</implement>', t, re.DOTALL)
    found_dict = dict(found)
    pprint(found_dict)
    return found_dict
