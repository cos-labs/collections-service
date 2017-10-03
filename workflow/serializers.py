# -*- coding: utf-8 -*-
"""Workflow Serializers"""


from rest_framework.serializers import CharField, ModelSerializer, JSONField, raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_framework_json_api.relations import ResourceRelatedField, SerializerMethodResourceRelatedField
from django.contrib.auth.models import User, Group

from workflow import models


class Workflow(ModelSerializer):

    initialization_values = JSONField(required=False)

    included_serializers = {
        'sections': 'workflow.serializers.Section',
        'widgets': 'workflow.serializers.Widget',
        'cases': 'workflow.serializers.Case',
        'parameter_aliases': 'workflow.serializers.ParameterAlias',
        'parameters': 'workflow.serializers.Parameter',
        'parameter_stubs': 'workflow.serializers.ParameterStub'
    }

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

    class JSONAPIMeta:
        included_resources = [
            'sections',
            'widgets',
            'case',
            'parameter_aliases',
            'parameters',
            'parameter_stub'
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

    included_serializers = {
        'parameters': 'workflow.serializers.Parameter',
        'widget': 'workflow.serializers.Widget',
        'cases': 'workflow.serializers.Case'
    }

    parameter_stub = ResourceRelatedField(
        queryset=models.Parameter.objects.all(),
        many=False,
        required=False
    )

    cases = ResourceRelatedField(
        queryset=models.Case.objects.all(),
        many=True,
        required=False
    )

    parameters = SerializerMethodResourceRelatedField(
        read_only=True,
        source='get_parameters',
        model=models.Parameter,
        many=True,
        required=False
    )

    def get_parameters(self, obj):
        return models.Parameter.objects.filter(name=obj.parameter_stub.name)

    class Meta:
        resource_name = 'parameter-aliases'
        model = models.ParameterAlias
        fields = [
            'id',
            'alias',
            'widget',
            'parameters',
            'cases',
            'parameter_stub',
            'workflow',
        ]

    class JSONAPIMeta:
        included_resources = [
            'parameters',
            'widget',
            'cases'
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

    cases = ResourceRelatedField(
        queryset=models.Case.objects.all(),
        many=True,
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

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        for attr, value in validated_data.items():

            # THIS NEEDS TESTING
            if attr in info.relations and info.relations[attr].has_through_model:
                for related_instance in value:
                    through_class = info.relations[attr].model_field.rel.through
                    through_instance = through_class()
                    existing_through_instances = through_class.objects.filter(**{
                        info.relations[attr].model_field.m2m_field_name()+"_id": instance.id
                    }).filter(**{
                        info.relations[attr].model_field.m2m_reverse_field_name()+"_id": related_instance.id
                    })
                    if existing_through_instances.exists():
                        continue
                    setattr(through_instance, info.relations[attr].model_field.m2m_field_name(), instance)
                    setattr(through_instance, info.relations[attr].model_field.m2m_reverse_field_name(), related_instance)
                    through_instance.save()

            elif attr in info.relations and info.relations[attr].to_many:
                set_many(instance, attr, value)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance

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
            'cases',
            'workflow'
        ]


class Case(ModelSerializer):

    included_serializers = {
        'workflow': 'workflow.serializers.Workflow',
        'sections': 'workflow.serializers.Section',
        'widgets': 'workflow.serializers.Widget',
        'parameter_aliases': 'workflow.serializers.ParameterAlias',
        'parameters': 'workflow.serializers.Parameter',
        'stubs': 'workflow.serializers.ParameterStub'
    }

    workflow = ResourceRelatedField(
        queryset=models.Workflow.objects.all(),
        many=False,
        required=True
    )

    sections = ResourceRelatedField(
        queryset=models.Section.objects.all(),
        many=True,
        required=False
    )

    widgets = ResourceRelatedField(
        queryset=models.Widget.objects.all(),
        many=True,
        required=False
    )

    parameter_aliases = ResourceRelatedField(
        queryset=models.ParameterAlias.objects.all(),
        many=True,
        required=False
    )

    parameters = ResourceRelatedField(
        queryset=models.Parameter.objects.all(),
        many=True,
        required=False
    )

    stubs = ResourceRelatedField(
        queryset=models.ParameterStub.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        resource_name = 'cases'
        model = models.Case
        fields = [
            'id',
            'workflow',
            'sections',
            'widgets',
            'parameter_aliases',
            'parameters',
            'stubs'
        ]

    class JSONAPIMeta:
        included_resources = [
            'workflow',
            'sections',
            'widgets',
            'parameter_aliases',
            'parameters',
            'stubs'
        ]
