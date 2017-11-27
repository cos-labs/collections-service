# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.contrib import rdb

import tika
from tika import parser
import requests

@shared_task
def update_item(self, instance_type, instance_id,  backend):
    instance = instance_type.objects.get(id=instance_id)
    requests.get(instance.file_link)
    parsed =  parser.from_file(file_path)['content']
    instance.content = parsed["content"]
    backend.update(self, [instance])
