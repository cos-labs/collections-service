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


class ParameterMapping(viewsets.ModelViewSet):
    queryset = models.ParameterMapping.objects.all()
    serializer_class = serializers.ParameterMapping

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
