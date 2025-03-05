import os
import tomllib

config_file_name = '.unitai.toml'
doc_url = 'https://github.com/santinic/unitai'


def read_config():
    if os.getenv('UNITAI_CONFIG'):
        file_path = os.getenv('UNITAI_CONFIG')
    else:
        file_path = os.path.join(os.path.dirname(__file__), '..', config_file_name)
    if not os.path.exists(file_path):
        raise Exception(f'No {file_path} config file found.')
    print(f'Reading {file_path} config')
    with open(file_path, 'r') as file:
        config = tomllib.loads(file.read())
        return config


def config_get_or(section, key, default=None):
    if section not in config:
        raise f'Section [{section}] not found in {config_file_name}. Please check documentation: {doc_url}'
    if key in config[section]:
        return config[section][key]
    return default


config = read_config()
