#!/usr/bin/env python
import os
import sys
import random

proj_path = "."
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings.dev")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from tests import factories
from api import models
import datetime
import pytz


owner = models.User.objects.get(pk=3)

meetings = factories.MeetingFactory.build_batch(10, created_by=owner)

names = []

with open('tests/diverse_names.txt') as name_file:
    content = name_file.readlines()
    content = [x.strip() for x in content]
    names = [(x.split(' ')[0], ' '.join(x.split(' ')[1:])) for x in content]


for m in meetings:
    m.save()
    print("New meeting: " + m.title)
    users = [owner]
    for x in range(0,9):
        name = random.choice(names)
        f_name = name[0]
        l_name = name[1]
        users.append(factories.UserFactory(first_name=f_name, last_name=l_name))
    ctr = 0
    for u in users:
        if not models.User.objects.all().filter(username=u.username).exists():
            print("new user: " + u.username)
            u.save()
        else:
            u = models.User.objects.get(username=u.username)
        items = factories.ItemFactory.build_batch(10, collection=m, created_by=u)
        for i in items:
            print("new item: " + i.title)
            i.status = random.choice(
                ['approved', 'approved', 'approved', 'approved', 'pending', 'pending', 'rejected'])
            i.category = 'presentation'
            i.type = 'event'
            i.start_time = m.start_datetime + datetime.timedelta(0, 0, 0, 0, 0, ctr)
            i.end_time = i.start_time + datetime.timedelta(0, 0, 0, 0, 0, 1)
            i.location = 'Room ' + random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'])
            i.date_submitted = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
            i.date_accepted = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))

            i.save()
            if ctr == 10:
                ctr = 0
            else:
                ctr += 1
