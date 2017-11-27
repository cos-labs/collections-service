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
    token = instance.created_by.socialaccount_set.all()[0].socialtoken_set.all()[0].token
    res = requests.get(instance.file_link, headers={
        'authorization': "Bearer " + token,
    })

    if res.status_code == 401:
        # Probably the file is not public
        pass
    parsed = parser.from_buffer(res.content)
    instance.content = parsed["content"]
    backend.update(self, [instance])
