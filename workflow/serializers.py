# -*- coding: utf-8 -*-
"""Workflow Serializers"""


from rest_framework.serializers import CharField, ModelSerializer, JSONField
from rest_framework_json_api.relations import ResourceRelatedField, SerializerMethodResourceRelatedField
from django.contrib.auth.models import User, Group

from workflow import models


class Workflow(ModelSerializer):

    initialization_values = JSONField(required=False)

    class Meta:
        resource_name = 'workflow'
        model = models.Workflow
        fields = [
            'id',
            'title',
            'description',
            'initialization_values',
            'workflow_config',
            'sections',
            'widgets',
            'parameter_aliases',
            'parameter_stubs',
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
            'index',
            'workflow',
            'widgets'
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
            'index',
            'parameter_aliases',
            'section',
            'workflow',
        ]


class ParameterAlias(ModelSerializer):

    parameter_stub = ResourceRelatedField(
        queryset=models.Parameter.objects.all(),
        many=False,
        required=False
    )

    parameter = SerializerMethodResourceRelatedField(
        read_only=True,
        source='get_parameter',
        model=models.Parameter,
        many=False,
        required=False
    )

    def get_parameter(self, obj):
        if obj.parameter_stub.scope != 'CASE':
            return models.Parameter.objects.get(name=obj.parameter_stub.name)
        case_pk = self._context['request']._request.resolver_match.kwargs['case_pk']
        return models.Parameter.objects.filter(case__id=case_pk).get(name=obj.parameter_stub.name)

    class Meta:
        resource_name = 'parameter-aliases'
        model = models.ParameterAlias
        fields = [
            'id',
            'alias',
            'widget',
            'parameter',
            'parameter_stub',
            'workflow',
        ]


class ParameterStub(ModelSerializer):

    aliases = ResourceRelatedField(
        queryset=models.ParameterAlias.objects.all(),
        many=True,
        required=False,
    )

    workflow = ResourceRelatedField(
        queryset=models.Workflow.objects.all(),
        many=False,
        required=True
    )

    class Meta:
        resource_name = 'parameter-stubs'
        model = models.ParameterStub
        fields = [
            'id',
            'name',
            'scope',
            'workflow',
            'parameters',
            'aliases'
        ]


class Parameter(ModelSerializer):

    #included_serializers = {
    #    'aliases': 'workflow.serializers.ParameterAlias'
    #}

    properties = JSONField(required=False)
    value = JSONField(required=False)

    case = ResourceRelatedField(
        queryset=models.Case.objects.all(),
        many=False,
        required=False
    )

    workflow = ResourceRelatedField(
        queryset=models.Workflow.objects.all(),
        many=False,
        required=True
    )

    stub = ResourceRelatedField(
        queryset=models.ParameterStub.objects.all(),
        required=False,
        many=False
    )

    aliases = SerializerMethodResourceRelatedField(
        read_only=True,
        source='get_aliases',
        model=models.ParameterAlias,
        many=True,
        required=False
    )

    def get_aliases(self, obj):
        if not obj.stub:
            return models.ParameterAlias.objects.none()
        return obj.stub.aliases.all()

    class Meta:
        resource_name = 'parameters'
        model = models.Parameter
        fields = [
            'id',
            'name',
            'value',
            'properties',
            'aliases',
            'stub',
            'case',
            'workflow'
        ]


class Case(ModelSerializer):

    parameters = ResourceRelatedField(
        queryset=models.Parameter.objects.all(),
        many=True,
        required=False
    )

    workflow = ResourceRelatedField(
        queryset=models.Workflow.objects.all(),
        many=False,
        required=True
    )

    class Meta:
        resource_name = 'cases'
        model = models.Case
        fields = [
            'id',
            'workflow',
            'parameters'
        ]
