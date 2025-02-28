import os
import tomllib


def read_config():
    if os.getenv('UNITAI_CONFIG'):
        file_path = os.getenv('UNITAI_CONFIG')
    else:
        file_path = os.path.join(os.path.dirname(__file__), '..', '.unitai.toml')
    if not os.path.exists(file_path):
        raise Exception(f'No {file_path} config file found.')
    print(f'Reading {file_path} config')
    with open(file_path, 'r') as file:
        config = tomllib.loads(file.read())
        print('Using model', config['ai']['model'])
        return config


config = read_config()
