# -*- coding: utf-8 -*-
"""Workflow Models"""

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField


class Workflow(models.Model):
    """Workflow Model"""

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, blank=False)
    description = models.TextField(null=False, blank=True)
    initialization_values = JSONField(default={})
    workflow_config = JSONField(default={})
    case_description = models.TextField(null=False, blank=True, default="")

    class Meta:
        permissions = [
            ("read", "read"),
            ("execute", "execute")
        ]

    class JSONAPIMeta:
        resource_name = 'workflows'

    def __str__(self):
        return self.title


class Section(models.Model):
    """Section Model"""

    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(null=False, blank=True)
    index = models.IntegerField(null=True, blank=True)

    workflow = models.ForeignKey(
        'Workflow',
        related_name='sections',
        null=False
    )

    cases = models.ManyToManyField(
        'Case',
        related_name="sections",
        blank=True
    )

    class JSONAPIMeta:
        resource_name = 'sections'

    def __str__(self):
        return self.label


class Widget(models.Model):
    """Widget Model"""

    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    widget_type = models.CharField(max_length=24, blank=False, null=False)
    index = models.IntegerField(null=True, blank=True)

    section = models.ForeignKey(
        'Section',
        related_name='widgets',
        null=False
    )

    workflow = models.ForeignKey(
        'Workflow',
        related_name='widgets',
        null=False
    )

    cases = models.ManyToManyField(
        'Case',
        related_name="widgets",
        blank=True
    )

    class JSONAPIMeta:
        resource_name = 'widgets'

    def __str__(self):
        return self.label


class ParameterAlias(models.Model):
    """ParameterAlias Model"""

    id = models.AutoField(primary_key=True)
    alias = models.CharField(max_length=64, blank=False, null=False)

    widget = models.ForeignKey(
        'Widget',
        related_name='parameter_aliases',
        null=True
    )

    parameter_stub = models.ForeignKey(
        'ParameterStub',
        related_name='aliases',
        null=True
    )

    workflow = models.ForeignKey(
        'Workflow',
        related_name='parameter_aliases',
        null=False
    )

    cases = models.ManyToManyField(
        'Case',
        related_name="parameter_aliases",
        blank=True
    )

    class JSONAPIMeta:
        resource_name = 'parameter-aliases'

    def __str__(self):
        return self.alias


class ParameterStub(models.Model):
    """ParameterStub Model"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=False)
    scope = models.CharField(
        max_length=8,
        blank=False,
        default='CASE',
        choices=[
            ('CASE', 'Case'),
            ('WORKFLOW', 'Workflow'),
            ('GLOBAL', 'Global')
        ]
    )

    cases = models.ManyToManyField(
        'Case',
        related_name='stubs',
        through="CaseStub",
        blank=True
    )

    workflow = models.ForeignKey(
        'Workflow',
        related_name='parameter_stubs',
        null=False
    )

    class Meta:
        unique_together = ('workflow', 'name')

    class JSONAPIMeta:
        resource_name = 'parameter-stubs'

    def __str__(self):
        return self.name


class Parameter(models.Model):
    """Parameter Model"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=False)
    value = JSONField(null=True, blank=True, default=None)
    properties = JSONField(null=True, blank=True, default={})

    stub = models.ForeignKey(
        'ParameterStub',
        related_name='parameters',
        null=True,
        blank=True
    )

    cases = models.ManyToManyField(
        'Case',
        related_name='parameters',
        through="CaseParameter",
        blank=True
    )

    workflow = models.ForeignKey(
        'Workflow',
        related_name='parameters',
        null=False
    )

    class JSONAPIMeta:
        resource_name = 'parameters'

    def __str__(self):
        return str(self.id)


class CaseParameter(models.Model):
    """Context"""

    id = models.AutoField(primary_key=True)

    case = models.ForeignKey(
        "Case",
        related_name="case_parameters",
        null=True
    )

    parameter = models.ForeignKey(
        "Parameter",
        related_name="case_parameters",
        null=True
    )

    class Meta:
        unique_together = ('case', 'parameter')

    def __str__(self):
        return "<CaseParameter: " + str(self.id) + " [" + str(self.case.id) + " : " + str(self.parameter.id) + "]>"


class CaseStub(models.Model):
    """Context"""

    id = models.AutoField(primary_key=True)

    case = models.ForeignKey(
        "Case",
        related_name="case_stubs",
        null=True
    )

    stub = models.ForeignKey(
        "ParameterStub",
        related_name="case_stubs",
        null=True
    )

    class Meta:
        unique_together = ('case', 'stub')

    def __str__(self):
        return "<CaseStub: " + str(self.id) + " [" + str(self.case.id) + " : " + str(self.stub.id) + "]>"


class Case(models.Model):
    """Case Model"""

    id = models.AutoField(primary_key=True)

    workflow = models.ForeignKey(
        'Workflow',
        related_name='cases',
        null=False
    )

    collection = models.ForeignKey(
        'api.Collection',
        related_name='collection',
        null=True
    )

    class Meta:
        permissions = [
            ("read", "read"),
            ("execute", "execute")
        ]

    class JSONAPIMeta:
        resource_name = 'cases'

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
