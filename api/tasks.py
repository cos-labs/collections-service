# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

import tika
from tika import parser

@shared_task
def do_update(instance, self, backend):
    backend.update(self, [instance])


@shared_task
def scrape_text(file_handle):
    import ipdb; ipdb.set_trace()
    parsed = parser.from_file('/path/to/file')
    print(parsed["metadata"])
    print(parsed["content"])
