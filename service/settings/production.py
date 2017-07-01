
from __future__ import absolute_import, unicode_literals

from .base import *


DEBUG=False
STATIC_URL = 'https://cos-labs.github.io/collections-service/'

try:
    from .local import *
except ImportError:
    print("Attention: No Local Settings Defined.")
    pass

