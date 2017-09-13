from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField


class Workflow(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, blank=False)
    description = models.TextField(null=False, blank=True)
    initialization_values = JSONField()


class Section(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(null=False, blank=True)
    workflow = models.ForeignKey('Workflow', related_name='sections', null=False)


class Widget(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    widget_type = models.CharField(max_length=24, blank=False, null=False)
    parameter_mappings = models.ManyToManyField('WidgetParameterMapping', related_name='consumer_widgets')
    section = models.ForeignKey('Section', related_name='widgets', null=False)
    workflow = models.ForeignKey('Workflow', related_name='widgets', null=False)


class WidgetParameterMapping(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=False, null=False)
    parameter = models.ForeignKey('Parameter', related_name='widget_parameter_mappings', null=True)
    workflow = models.ForeignKey('Workflow', related_name='widget_parameter_mappings', null=False)


class Parameter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, blank=False)
    value = JSONField()
    properties = JSONField()
    case = models.ForeignKey('Case', null=True)
    workflow = models.ForeignKey('Workflow', related_name='parameters', null=False)

    class Meta:
        unique_together = ('case', 'name')


class Case(models.Model):
    id = models.AutoField(primary_key=True)
    workflow = models.ForeignKey('Workflow', related_name='cases')
