# coding=utf-8

try:
    from .local import *
except ImportError:
    raise NotImplementedError(
        'Start your WSGI server with needed settings'
        ' or provide settings/local.py (for development only).'
    )
