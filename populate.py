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
    CollectionGroup,
    CollectionWorkflow,
    Item,
    User
)
from workflow.models import (
    Workflow,
    Section,
    Widget,
    Parameter,
    ParameterStub,
    ParameterAlias
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


# Make a public group

try:
    public_group = Group.objects.get(name="public")
except:
    public_group = Group()
    public_group.name = "public"
    public_group.save()


# Setup Workflows
# ##############################################################################

# Workflows need to happen before the collections so that collections can have a
# submission workflow associated with them.

# Load the needed workflows. `workflows` is modified here.
workflows = {
    "meeting": "meeting.json",
    "meeting-approval": "meeting-approval.json",
    "dataset": "dataset.json",
    "dataset-approval": "dataset-approval.json"
}

for workflow_name, workflow_schema in workflows.items():

    with open('workflow/schemas/' + workflow_schema) as data_file:
        wf_config = json.load(data_file)

    workflow = Workflow()
    workflow.title = wf_config.get("title", "")
    workflow.description = wf_config.get("description", "")
    workflow.case_description = wf_config.get("case_description", "")
    workflow.initialization_values = wf_config.get("initialParameters", {})
    workflow.save()

    for name, value in wf_config.get("initialParameters", {}).items():

        try:
            parameter_stub = ParameterStub.objects\
                .filter(workflow_id=workflow.id).get(name=name)
        except:
            parameter_stub = ParameterStub()

        parameter_stub.name = name
        parameter_stub.scope = "WORKFLOW"
        parameter_stub.workflow = workflow
        parameter_stub.save()

        parameter = Parameter()
        parameter.name = name
        parameter.value = value.get('value', None)
        parameter.properties = value.get('properties', None)
        parameter.stub = parameter_stub
        parameter.workflow = workflow
        parameter.save()

    section_index = 0
    for section_config in wf_config.get("sections", []):
        section_index += 1

        section = Section()
        section.label = section_config.get("label", "")
        section.description = section_config.get("description", "")
        section.index = section_index
        section.workflow = workflow

        section.save()

        widget_index = 0
        for widget_config in section_config.get("widgets", []):
            widget_index += 1

            widget = Widget()
            widget.label = widget_config.get("label", "")
            widget.description = widget_config.get("description", "")
            widget.widget_type = widget_config.get("widgetType", "")
            widget.index = widget_index
            widget.workflow = workflow
            widget.section = section

            widget.save()

            for alias, parameter_name in\
                widget_config.get("parameters", {}).items():

                parameter_alias = ParameterAlias()

                try:
                    parameter_stub = ParameterStub.objects\
                        .filter(workflow_id=workflow.id)\
                        .get(name=parameter_name)
                except:
                    parameter_stub = ParameterStub()
                    parameter_stub.scope = "CASE"

                parameter_alias.alias = alias
                parameter_alias.workflow = workflow
                parameter_alias.widget = widget

                parameter_stub.name = parameter_name
                parameter_stub.workflow = workflow
                parameter_stub.save()

                parameter_alias.parameter_stub = parameter_stub
                parameter_alias.save()

                parameter_stub.aliases.add(parameter_alias)

            section.widgets.add(widget)

        workflow.sections.add(section)

    workflows[workflow_name] = workflow


meetings_next_workflow_param = workflows["meeting"].parameters.get(name="next-workflow")
meetings_next_workflow_param.value = workflows["meeting-approval"].id
meetings_next_workflow_param.save()

datasets_next_workflow_param = workflows["dataset"].parameters.get(name="next-workflow")
datasets_next_workflow_param.value = workflows["dataset-approval"].id
datasets_next_workflow_param.save()

# Create Collections
# ##############################################################################


# Create the meetings and talks/posters in them

meetings = factories.MeetingFactory.build_batch(5, created_by=su)
datasets = factories.DatasetFactory.build_batch(5, created_by=su)
names = []

with open('tests/diverse_names.txt') as name_file:
    content = name_file.readlines()
    content = [x.strip() for x in content]
    names = [(x.split(' ')[0], ' '.join(x.split(' ')[1:])) for x in content]


for c in meetings + datasets:
    c.save()
    print("New " + c.collection_type + ": " + c.title)
    users = [su]
    for x in range(0,9):
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
        items = factories.ItemFactory.build_batch(10, collection=c, created_by=u)
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
                i.start_time = c.start_datetime + datetime.timedelta(0, 0, 0, 0, 0, ctr)
                i.start_time = i.start_time.replace(hour=8, minute=0)
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

            if c.collection_type == "dataset":
                i.file_name = "test." + str(random.randint(0,100000)) + "." + \
                             random.choice(["pdf", "png", "docx", "ppx", "odt", "tif", "jpg", "zip"])

            i.save()
            assign_perm("view", public_group, i)
            if ctr == 10:
                ctr = 0
            else:
                ctr += 1

    if c.collection_type == "meeting":
        CollectionWorkflow.objects.create(
            role="submission",
            collection=c,
            workflow=workflows["meeting"],
            #authorized_groups=public_group
        )

    elif c.collection_type == "dataset":
        CollectionWorkflow.objects.create(
            role="submission",
            collection=c,
            workflow = workflows["dataset"],
            #authorized_groups=public_group
        )

    assign_perm("view_collection", public_group, c)
    assign_perm("add_item", public_group, c)
    c.save()


# EOF
# ##############################################################################
