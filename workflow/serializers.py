# -*- coding: utf-8 -*-
"""Workflow Serializers"""


from rest_framework.serializers import CharField, ModelSerializer, JSONField, raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_framework_json_api.relations import ResourceRelatedField, SerializerMethodResourceRelatedField
from django.contrib.auth.models import User, Group

from collections import Mapping, OrderedDict
from rest_framework.fields import get_error_detail, set_value
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.fields import empty
from workflow import models
from rest_framework.fields import SkipField

class MyRRField(ResourceRelatedField):

    def validate_empty_values(self, data):
        """
        Validate empty values, and either:
        * Raise `ValidationError`, indicating invalid data.
        * Raise `SkipField`, indicating that the field should be ignored.
        * Return (True, data), indicating an empty value that should be
          returned without any further validation being applied.
        * Return (False, data), indicating a non-empty value, that should
          have validation applied as normal.
        """
        #import ipdb; ipdb.set_trace()
        if self.read_only:
            return (True, self.get_default())

        if data is empty:
            if getattr(self.root, 'partial', False):
                raise SkipField()
            if self.required:
                self.fail('required')
            return (True, self.get_default())

        if data is None:
            if not self.allow_null:
                self.fail('null')
            return (True, None)

        return (False, data)

    def run_validation(self, data=empty):
        """
        Validate a simple representation and return the internal value.
        The provided data may be `empty` if no representation was included
        in the input.
        May raise `SkipField` if the field should not be included in the
        validated data.
        """


        if data == '':
            data = None
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data
        value = self.to_internal_value(data)
        self.run_validators(value)
        return value

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

    stub = MyRRField(
        queryset=models.ParameterStub.objects.all(),
        required=False,
        many=False,
        allow_null=True
    )

    aliases = SerializerMethodResourceRelatedField(
        read_only=True,
        source='get_aliases',
        model=models.ParameterAlias,
        many=True,
        required=False
    )


    def create(self, validated_data):
        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:
            return ExampleModel.objects.create(**validated_data)
        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:
            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance
        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.objects.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():

                # THIS NEEDS TESTING
                if field_name in info.relations and info.relations[field_name].has_through_model:
                    field = info.relations[field_name].model_field
                    for related_instance in value:
                        through_class = field.rel.through
                        through_instance = through_class()
                        existing_through_instances = through_class.objects\
                            .filter(**{field.m2m_field_name()+"_id": instance.id})\
                            .filter(**{field.m2m_reverse_field_name()+"_id": related_instance.id})
                        if existing_through_instances.exists():
                            continue
                        setattr(through_instance, field.m2m_field_name(), instance)
                        setattr(through_instance, field.m2m_reverse_field_name(), related_instance)
                        through_instance.save()

                else:
                    set_many(instance, field_name, value)
        return instance

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
                field = info.relations[attr].model_field
                for related_instance in value:
                    through_class = field.rel.through
                    through_instance = through_class()
                    existing_through_instances = through_class.objects\
                        .filter(**{field.m2m_field_name()+"_id": instance.id})\
                        .filter(**{field.m2m_reverse_field_name()+"_id": related_instance.id})
                    if existing_through_instances.exists():
                        continue
                    setattr(through_instance, field.m2m_field_name(), instance)
                    setattr(through_instance, field.m2m_reverse_field_name(), related_instance)
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
