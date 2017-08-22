from __future__ import absolute_import, unicode_literals

import os
import dj_database_url

from .base import *

ALLOWED_HOSTS = [
    'osf-collections.herokuapp.com',
    'dev-labs-2.cos.io',
    '*'
]

CORS_ORIGIN_ALLOW_ALL = True
CSRF_TRUSTED_ORIGINS = ['dev-labs-2.cos.io']

DEBUG=True
SECRET_KEY = os.environ['SECRET_KEY']
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = 'https://cos-labs.github.io/collections-service/'

DATABASES = {}
DATABASES['default'] = dj_database_url.config()

try:
    from .local import *
except ImportError:
    print("Attention: No Local Settings Defined.")
    pass

