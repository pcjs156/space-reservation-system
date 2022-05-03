import functools


def check_not_null(*variables):
    return functools.reduce(lambda x, y: x is not None and y is not None, variables)
