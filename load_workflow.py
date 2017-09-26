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

wf_config = {
  "title": "Dataset Submission Form",
  "description": "The dataset submission form allows users to submit data to a data repository.",
  "initialParameters": {
    "event-creation-choices": {
      "value": [
        {
          "label": "Use an existing node",
          "parameter": "useExistingNode"
        },
        {
          "label": "Create a new node",
          "parameter": "createNewNode"
        }
      ]
    }
  },
  "sections": [
    {
      "label": "Upload Data",
      "widgets": [
        {
          "label": "Upload a file",
          "description": "Select the file to upload",
          "widgetType": "file-uploader",
          "parameters": {
            "fileData": "file-data",
            "fileName": "file-name"
          }
        },
        {
          "label": "Title",
          "description": "Enter the title of the file.",
          "widgetType": "text-field",
          "parameters": {
            "value": "title-widget"
          }
        }
      ]
    },
    {
      "label": "File Metadata",
      "description": "Enter the metadata for the file",
      "widgets": [
        {
          "label": "Metadata",
          "desciption": "Enter the metadata for the file that is being uploaded",
          "widgetType": "text-field",
          "parameters": {
            "value": "metadata",
          }
        },
      ]
    },
    {
      "label": "Submit",
      "description": "Submit this talk to the meeting",
      "widgets": [
        {
          "label": "Submit",
          "description": "Submit this talk",
          "widgetType": "meeting-submit",
          "parameters": {
            "title": "title-widget",
            "fileData": "file-data",
            "fileName": "file-name",
            "metadata": "metadata"
          }
        }
      ]
    }
  ]
}


workflow = models.Workflow()
workflow.title = wf_config.get("title", "")
workflow.description = wf_config.get("description", "")
workflow.initialization_values = wf_config.get("initialParameters", {})
workflow.save()

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

            parameter_alias.alias = alias
            parameter_alias.workflow = workflow

            parameter_stub.name = parameter_name
            parameter_stub.scope = "CASE"
            parameter_stub.workflow = workflow
            parameter_stub.save()

            parameter_alias.parameter_stub = parameter_stub
            parameter_alias.save()

            parameter_stub.aliases.add(parameter_alias)

        section.widgets.add(widget)

    workflow.sections.add(section)
