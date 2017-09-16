from django import forms
from django.contrib import admin
from workflow.models import Workflow, Section, Widget, ParameterAlias, ParameterStub, Parameter, Case

from django.contrib.admin import SimpleListFilter


class WorkflowListFilter(SimpleListFilter):
    """Filter an object list by workflow"""

    title = 'Workflow'
    parameter_name = 'workflow'
    default_value = None

    def lookups(self, request, model_admin):
        """Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar."""

        return sorted([(str(workflow.id), workflow.title)
            for workflow in Workflow.objects.all()])

    def queryset(self, request, queryset):
        """Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`."""

        if self.value():
            try:
                return queryset.filter(workflow_id=self.value())
            except FieldError:
                return queryset.filter(workflows=self.value())
        return queryset


class CaseListFilter(SimpleListFilter):
    """Filter an object list by workflow"""

    title = 'Case'
    parameter_name = 'case'
    default_value = None

    def lookups(self, request, model_admin):
        """Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar."""

        return sorted([(str(case.id), case.id)
            for case in Case.objects.all()])

    def queryset(self, request, queryset):
        """Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`."""

        if self.value():
            try:
                return queryset.filter(case_id=self.value())
            except FieldError:
                return queryset.filter(case=self.value())
        return queryset


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'title',
        'description'
    ]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):

    def get_workflow_name(self, object):
        return object.workflow.title

    get_workflow_name.admin_order_field = 'title'  # Allows column order sorting
    get_workflow_name.short_description = 'Workflow Title'  # Renames column head

    list_display = [
        'id',
        'label',
        'index',
        'get_workflow_name',
        'description'
    ]

    list_filter = [
        WorkflowListFilter
    ]


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'label',
        'widget_type',
        'description'
    ]

    list_filter = [
        WorkflowListFilter
    ]


@admin.register(ParameterAlias)
class ParameterAliasAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'alias'
    ]

    list_filter = [
        WorkflowListFilter
    ]


@admin.register(ParameterStub)
class ParameterStubAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'name'
    ]

    list_filter = [
        WorkflowListFilter
    ]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):


    def get_workflow_name(self, object):
        return object.workflow.title

    get_workflow_name.admin_order_field = 'title'  # Allows column order sorting
    get_workflow_name.short_description = 'Workflow Title'  # Renames column head


    def get_case_id(self, object):
        if object.case:
            return object.case.id
        return ''

    get_case_id.admin_order_field = 'id'
    get_case_id.short_description = 'case'

    list_display = [
        'id',
        'name',
        'value',
        'get_workflow_name',
        'get_case_id'
    ]

    list_filter = [
        WorkflowListFilter,
        CaseListFilter
    ]


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    def get_workflow_name(self, object):
        return object.workflow.title

    get_workflow_name.admin_order_field = 'title'  # Allows column order sorting
    get_workflow_name.short_description = 'Workflow Title'  # Renames column head

    list_display = [
        'id',
        'workflow'
    ]

    list_filter = [
        WorkflowListFilter
    ]
