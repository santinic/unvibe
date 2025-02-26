import os
import tomllib


def read_config():
    config_file = '.unitai.toml'
    # config_file_abs_path = os.path.join(os.path.expanduser('~'), config_file)
    config_file_abs_path = os.path.join('..', config_file)
    if not os.path.exists(config_file_abs_path):
        raise Exception(f'No {config_file_abs_path} config file found.')
    print(f'Reading {config_file_abs_path} config')
    with open(config_file_abs_path, 'r') as file:
        config = tomllib.loads(file.read())
        return config


config = read_config()
