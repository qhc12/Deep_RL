import sys


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
