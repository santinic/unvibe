import redis
from termcolor import colored

from .config import config
import anthropic
from openai import OpenAI

redis_client = redis.Redis(host=config['cache']['host'], port=config['cache']['port'], db=config['cache']['db'])
redis_client.ping()


def redis_cached(func):
    """redis memoization for functions"""

    def wrapper(*args, **kwargs):
        key = f'{func.__name__}__{args}__{kwargs}'
        if redis_client.exists(key):
            print('Return cached', key)
            bytes = redis_client.get(key)
            result = bytes.decode('utf-8')
        else:
            result = func(*args, **kwargs)
            redis_client.set(key, result)
            redis_client.expire(key, config['cache']['expire'])
        print(colored('LLM OUTPUT:', result, 'blue'))
        return result

    return wrapper


@redis_cached
def call_openai(system, prompt):
    client = OpenAI(api_key=config['ai']['api_key'], base_url=config['ai']['base_url'])
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
        # From deepseek.com:
        # USE CASE                  TEMPERATURE
        # Coding / Math:	                0.0
        # Data Cleaning / Data Analysis:    1.0
        # General Conversation:	            1.3
        # Translation:                      1.3
        # Creative Writing / Poetry:        1.5
        temperature=config['ai']['temperature'],
        stream=False
    )
    # print('llm resp.choices[0].message.content:', resp.choices[0].message.content)
    return resp.choices[0].message.content


@redis_cached
def call_claude(system, prompt):
    client = anthropic.Anthropic(api_key=config['ai']['api_key'])
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    )
    print('llm output:', message.content)
    return message.content[0].text


example = '''
<input implement="mul">
def mul(a, b):
    pass

assert mul(2, 3) == 6
print(mul(3.0, 2.1))  # 6.3
</input>
<output>
def mul(a, b):
    return a * b
</output>'''


def ai_call_one_function(func_name, context):
    system = "You only outpute code inside the <output> tag. No explanations before or after <output>"
    prompt = f'''
{example}
<input implement="{func_name}">
{context}
</input>
'''
    provider = config['ai']['provider']
    if provider == 'claude':
        resp_text = call_claude(system, prompt)
    elif provider == 'openai':
        resp_text = call_openai(system, prompt)
    else:
        raise NotImplementedError(f'{config.ai} not implemented')

    code = resp_text.split('<output>')[1].split('</output>')[0]
    print('AI <output>:', code)
    return code


def ai_call(func_name, context, failures):
    system = ("You only outpute code inside the <output> tag. No explanations before or after <output>. "
              "Only implement the requeste function. If <errors> tag is present, fix those errors.")
    errors_str = '\n'.join(failures) if failures else ''
    prompt = f'''{example}
<input implement="{func_name}">
{context}
</input>
{errors_str}
<output>
'''
    print('LLM PROMPT:', prompt)
    provider = config['ai']['provider']
    if provider == 'claude':
        resp_text = call_claude(system, prompt)
    elif provider == 'openai':
        resp_text = call_openai(system, prompt)
    else:
        raise NotImplementedError(f'{config.ai} not implemented')

    code = resp_text.split('<output>')[1].split('</output>')[0]
    return code
