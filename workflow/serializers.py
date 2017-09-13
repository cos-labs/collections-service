# -*- coding: utf-8 -*-
"""Workflow Serializers"""


from rest_framework.serializers import CharField, ModelSerializer
from rest_framework_json_api import serializers, relations
from django.contrib.auth.models import User, Group

from workflow import models


class Parameter(ModelSerializer):

    class Meta:
        resource_name = 'nets'
        model = models.Parameter
        fields = (
            'id',
            'name',
            'case',
            'value',
            'properties',
        )


class Case(serializers.ModelSerializer):

    class Meta:
        resource_name = 'case'
        model = models.Case
        fields = (
            'id'
        )
