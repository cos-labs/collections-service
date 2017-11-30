#!/usr/bin/env python

"""
A population script. Populates the database with the minimum needed database
entries required in order to run, in addition to populating the database with
basic example data; 10 collections with each 100 items.
"""



# Python Imports
# ##############################################################################

import os
import sys
import random
import json
import datetime
import pytz
from pprint import pprint


# Setup needed for Django
# ##############################################################################

# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings.dev")
proj_path = "."
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


# Library Imports
# ##############################################################################

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user
)
from allauth.socialaccount.models import SocialApp


# Local Imports
# ##############################################################################

from api.models import (
    Collection,
    Item,
    User
)

from tests import factories


# Populate data
# ##############################################################################


# Make a superuser
try:
    su = User.objects.get(id=2)
except:
    su = User.objects.create_superuser(
        settings.SU_USERNAME,
        settings.SU_EMAIL,
        settings.SU_PASSWORD
    )

# TODO: figure out why these 2 lines won't successfully set the SU's name
su.first_name = "Super"
su.last_name = "User"
su.save()


# Set up `Site` correctly

site = Site.objects.get(id=3)  # Why is it 3? I dono.... bcuz....
site.domain_name = "localhost:8000"
site.display_name = "localhost"
site.save()


# Set up the `SocialApp`

try:
    sa = SocialApp.models.get(
        provider=settings.SA_PROVIDER_NAME,
        sites__id=site.id
    )
except:
    sa = SocialApp()
    sa.provider = settings.SA_PROVIDER_NAME
    sa.name = settings.SA_APPLICATION_NAME
    sa.client_id = settings.SA_CLIENT_ID
    sa.secret = settings.SA_CLIENT_SECRET
    sa.save(force_insert=True)
    sa.sites.add(site)
    sa.save()

# Create Collections
# ##############################################################################


# Create the meetings and talks/posters in them

meetings = factories.MeetingFactory.build_batch(5, created_by=su)
repositories = factories.RepositoryFactory.build_batch(5, created_by=su)
names = []

with open('tests/diverse_names.txt') as name_file:
    content = name_file.readlines()
    content = [x.strip() for x in content]
    names = [(x.split(' ')[0], ' '.join(x.split(' ')[1:])) for x in content]


for c in meetings + repositories:
    c.showcased = False
    c.save()
    print("New " + c.collection_type + ": " + c.title)
    users = [su]
    for x in range(0,19):
        name = random.choice(names)
        f_name = name[0]
        l_name = name[1]
        users.append(factories.UserFactory(first_name=f_name, last_name=l_name))
    ctr = 0
    for u in users:
        if not User.objects.all().filter(username=u.username).exists():
            print("new user: " + u.username)
            u.save()
        else:
            u = User.objects.get(username=u.username)
        items = factories.ItemFactory.build_batch(2, collection=c, created_by=u)
        for i in items:
            print("new item: " + i.title)
            # Multiples of each status are to generate more appproved that other
            # statuses
            i.status = random.choice([
                'approved',
                'approved',
                'approved',
                'approved',
                'pending',
                'pending',
                'rejected'
            ])
            if c.collection_type == "meeting":
                i.category = 'presentation'
                i.kind = 'event'

                # import ipdb; ipdb.set_trace()
                i.start_time = c.start_datetime.replace(hour=8, minute=4)
                i.start_time = i.start_time + datetime.timedelta(0, 0, 0, 0, 0, ctr)
                i.end_time = i.start_time + datetime.timedelta(0, 0, 0, 0, 0, 1)
                i.location = 'Room ' + random.choice([
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'
                ])
                i.date_submitted = datetime.datetime\
                    .now(tz=pytz.timezone('US/Eastern'))
                i.date_accepted = datetime.datetime\
                    .now(tz=pytz.timezone('US/Eastern'))
                i.file_name = "test" + str(random.randint(0,100000)) + "." + \
                             random.choice(["pdf", "png", "docx", "ppx", "odt"])

            if c.collection_type == "repository":
                i.file_name = "test." + str(random.randint(0,100000)) + "." + \
                             random.choice(["pdf", "png", "docx", "ppx", "odt", "tif", "jpg", "zip"])

            i.save()
            if ctr == 10:
                ctr = 0
            else:
                ctr += 1

    c.save()


# EOF
# ##############################################################################
