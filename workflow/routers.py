# -*- coding: utf-8 -*-
"""Workflow Routers"""


from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers

from workflow import views

workflow_router = routers.SimpleRouter(trailing_slash=False)

workflow_router.register(r'workflows', views.Workflow)
workflow_router.register(r'sections', views.Section)
workflow_router.register(r'widgets', views.Widget)
workflow_router.register(r'widgetParameterMappings', views.WidgetParameterMapping)
workflow_router.register(r'parameters', views.Parameter)
workflow_router.register(r'cases', views.Case)

case_router = routers.NestedSimpleRouter(workflow_router, r'cases', lookup='case', trailing_slash=False)
case_router.register(r'parameters', views.Parameter, base_name='case-parameters')
