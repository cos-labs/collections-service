from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.helpers import ActionForm
from workflow.models import Workflow, Section, Widget, WidgetParameterMapping, Parameter, Case
from guardian.shortcuts import get_objects_for_user, assign_perm

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'workflow', 'description')

@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'widget_type', 'description')

@admin.register(WidgetParameterMapping)
class WidgetParameterMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'workflow', 'case')

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'workflow')
