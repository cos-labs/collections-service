from __future__ import absolute_import, unicode_literals

import os

from .base import *


DEBUG=False
SECRET_KEY = os.environ['SECRET_KEY']
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = 'https://cos-labs.github.io/collections-service/'


try:
    from .local import *
except ImportError:
    print("Attention: No Local Settings Defined.")
    pass

