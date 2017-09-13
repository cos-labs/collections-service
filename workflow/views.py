from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from workflow import models
from workflow import serializers


class Workflow(viewsets.ModelViewSet):
    queryset = models.Workflow.objects.all()
    serializer_class = serializers.Workflow

    def get_queryset(self):
        return self.queryset


class Section(viewsets.ModelViewSet):
    queryset = models.Section.objects.all()
    serializer_class = serializers.Section

    def get_queryset(self):
        return self.queryset


class Widget(viewsets.ModelViewSet):
    queryset = models.Widget.objects.all()
    serializer_class = serializers.Widget

    def get_queryset(self):
        return self.queryset


class WidgetParameterMapping(viewsets.ModelViewSet):
    queryset = models.WidgetParameterMapping.objects.all()
    serializer_class = serializers.WidgetParameterMapping

    def get_queryset(self):
        return self.queryset


class Parameter(viewsets.ModelViewSet):
    queryset = models.Parameter.objects.all()
    serializer_class = serializers.Parameter

    def get_queryset(self):
        return self.queryset


class Case(viewsets.ModelViewSet):
    queryset = models.Case.objects.all()
    serializer_class = serializers.Case
