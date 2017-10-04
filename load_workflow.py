#!/usr/bin/env python

import os
import sys

proj_path = "."
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings.dev")
sys.path.append(proj_path)
os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from workflow import models

import json
from pprint import pprint



with open('workflow/schemas/' + sys.argv[1]) as data_file:
    wf_config = json.load(data_file)

workflow = models.Workflow()
workflow.title = wf_config.get("title", "")
workflow.description = wf_config.get("description", "")
workflow.initialization_values = wf_config.get("initialParameters", {})
workflow.save()

for name, value in wf_config.get("initialParameters", {}).items():

    try:
        parameter_stub = models.ParameterStub.objects.filter(workflow_id=workflow.id).get(name=name)
    except:
        parameter_stub = models.ParameterStub()

    parameter_stub.name = name
    parameter_stub.scope = "WORKFLOW"
    parameter_stub.workflow = workflow
    parameter_stub.save()

    parameter = models.Parameter()
    parameter.name = name
    parameter.value = value.get('value', None)
    parameter.properties = value.get('properties', None)
    parameter.stub = parameter_stub
    parameter.workflow = workflow
    parameter.save()



section_index = 0
for section_config in wf_config.get("sections", []):
    section_index += 1

    section = models.Section()
    section.label = section_config.get("label", "")
    section.description = section_config.get("description", "")
    section.index = section_index
    section.workflow = workflow

    section.save()

    widget_index = 0
    for widget_config in section_config.get("widgets", []):
        widget_index += 1

        widget = models.Widget()
        widget.label = widget_config.get("label", "")
        widget.description = widget_config.get("description", "")
        widget.widget_type = widget_config.get("widgetType", "")
        widget.index = widget_index
        widget.workflow = workflow
        widget.section = section

        widget.save()

        for alias, parameter_name in widget_config.get("parameters", {}).items():

            parameter_alias = models.ParameterAlias()

            try:
                parameter_stub = models.ParameterStub.objects.filter(workflow_id=workflow.id).get(name=parameter_name)
            except:
                parameter_stub = models.ParameterStub()
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
