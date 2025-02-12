import redis
from .config import config

redis_client = redis.Redis(host=config['cache']['host'], port=config['cache']['port'], db=config['cache']['db'])
redis_client.ping()


def redis_cached(func):
    """cache in redis the results forever"""

    def wrapper(*args, **kwargs):
        key = f'{func.__name__}__{args}__{kwargs}'
        if redis_client.exists(key):
            print('Return cached', key)
            bytes = redis_client.get(key)
            return bytes.decode('utf-8')
        result = func(*args, **kwargs)
        redis_client.set(key, result)
        redis_client.expire(key, config['cache']['expiration'])
        return result

    return wrapper


@redis_cached
def call_claude(func_name, context):
    import anthropic
    client = anthropic.Anthropic(api_key=config['ai']['api_key'])
    system = "You only outpute code inside the <output> tag. No explanations before or after <output>"
    prompt = f'''
<input implement="mul">
def mul(a, b):
    pass

assert mul(2, 3) == 6
print(mul(3.0, 2.1))  # 6.3
</input>
<output>
def mul(a, b):
    return a * b
</output
<input implement="{func_name}">
{context}
</input>
'''
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system=system,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    )
    # print('system:', system)
    print('context:', context)
    print('llm output:', message.content)
    text = message.content[0].text
    code = text.split('<output>')[1].split('</output>')[0]
    print('code:', code)
    return code


def ai_call(func_name, context):
    if config['ai']['provider'] == 'claude':
        return call_claude(func_name, context)
    else:
        raise NotImplementedError(f'{config.ai} not implemented')
