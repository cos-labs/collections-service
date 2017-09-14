# -*- coding: utf-8 -*-
"""Workflow Serializers"""


from rest_framework.serializers import CharField, ModelSerializer
from rest_framework_json_api import serializers, relations
from django.contrib.auth.models import User, Group

from workflow import models


class Workflow(ModelSerializer):

    class Meta:
        resource_name = 'workflow'
        model = models.Workflow
        fields = [
            'id',
            'title',
            'description',
            'initialization_values',
            'sections',
            'widgets',
            'widget_parameter_mappings',
            'parameters',
            'cases'
        ]


class Section(ModelSerializer):

    class Meta:
        resource_name = 'sections'
        model = models.Section
        fields = [
            'id',
            'label',
            'description',
            'workflow',
            'widgets',
            'index'
        ]


class Widget(ModelSerializer):

    class Meta:
        resource_name = 'widgets'
        model = models.Widget
        fields = [
            'id',
            'label',
            'description',
            'widget_type',
            'widget_parameter_mappings',
            'section',
            'workflow',
            'index'
        ]


class WidgetParameterMapping(ModelSerializer):

    class Meta:
        resource_name = 'widget-parameter-mappings'
        model = models.WidgetParameterMapping
        fields = [
            'id',
            'name',
            'parameter',
            'workflow',
            'widget'
        ]


class Parameter(ModelSerializer):

    class Meta:
        resource_name = 'parameters'
        model = models.Parameter
        fields = [
            'id',
            'name',
            'value',
            'properties',
            'case',
            'workflow',
            'widget_parameter_mappings'
        ]


class Case(ModelSerializer):

    class Meta:
        resource_name = 'cases'
        model = models.Case
        fields = [
            'id',
            'workflow',
            'parameters'
        ]
