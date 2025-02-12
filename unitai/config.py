import json
import os


def read_config():
    config_file = '.unitai.json'
    config_file_abs_path = os.path.join(os.path.expanduser('~'), config_file)
    if not os.path.exists(config_file_abs_path):
        raise Exception(f'No {config_file_abs_path} config file found.')
    print(f'Reading {config_file_abs_path} config')
    with open(config_file_abs_path, 'r') as file:
        config = json.load(file)
        return config


config = read_config()
