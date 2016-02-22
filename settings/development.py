# coding=utf-8

from base import *

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += ('debug_toolbar',)

STATICFILES_DIRS = [STATIC_ROOT]
STATIC_ROOT = None
