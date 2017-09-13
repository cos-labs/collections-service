# -*- coding: utf-8 -*-
"""REST API URLs"""


from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_nested import routers

from workflow import views

workflow_router = routers.SimpleRouter(trailing_slash=False)

workflow_router.register(r'workflows', views.Workflow)
workflow_router.register(r'sections', views.Section)
workflow_router.register(r'widgets', views.Widget)
workflow_router.register(r'widget-parameter-mappings', views.WidgetParameterMapping)
workflow_router.register(r'parameters', views.Parameter)
workflow_router.register(r'cases', views.Case)

