import sys


def log(*args, **kwargs):
    # print('[UnitAI]', *args, **kwargs)
    print(*args, **kwargs)  # file=sys.stderr
