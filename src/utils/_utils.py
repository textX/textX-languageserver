# Copyright 2017 Palantir Technologies, Inc.
import os
import functools
import threading
import imp


def debounce(interval_s):
    """Debounce calls to this function until interval_s seconds have passed."""
    def wrapper(func):
        @functools.wraps(func)
        def debounced(*args, **kwargs):
            if hasattr(debounced, '_timer'):
                debounced._timer.cancel()
            debounced._timer = threading.Timer(interval_s, func, args, kwargs)
            debounced._timer.start()
        return debounced
    return wrapper


def exec_func_from_module(path_to_module, module_name):
    try:
        func_name = path_to_module[2:].split(':')[1]
        path_name = path_to_module.replace(':{}'.format(func_name), '')
        module = imp.load_source(module_name, path_name)
        return getattr(module, func_name)()
    except:
        return None


def flatten(list_of_lists):
    return [item for lst in list_of_lists for item in lst]


def line_col_to_pos(source, position):
    line = position['line']
    col = position['character']

    lines = source.splitlines()
    offset = 0
    for l in range(0, line):
        offset += (len(lines[l]) + 2)
    offset += col

    return offset


def pos_to_line_col(source, pos):
    line = 0
    lines = source.splitlines()
    for _ in lines:
        temp = pos - (len(lines[line]) + 2)
        if temp >= 0:
            pos = temp
            line += 1

    return line, pos
