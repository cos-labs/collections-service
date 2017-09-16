from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
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


class ParameterAlias(viewsets.ModelViewSet):

    queryset = models.ParameterAlias.objects.all()
    serializer_class = serializers.ParameterAlias

    def get_queryset(self):
        return self.queryset


class ParameterStub(viewsets.ModelViewSet):

    queryset = models.ParameterStub.objects.all()
    serializer_class = serializers.ParameterStub


class Parameter(viewsets.ModelViewSet):

    queryset = models.Parameter.objects.all()
    serializer_class = serializers.Parameter

    def retrieve(self, request, pk=None, case_pk=None):
        if not pk:
            try:
                pk = self.queryset.filter(case__id=case_pk).get(name=self.request.query_params['name']).id
                self.kwargs['pk'] = pk
            except:
                return Response({"data": None}, status=404)
        return super().retrieve(request, pk=pk)

    def get_queryset(self):
        queryset = self.queryset
        if self.kwargs['case_pk']:
            case = models.Case.objects.get(id=self.kwargs['case_pk'])
            queryset = queryset.filter(case__id=case.id) | queryset.filter(workflow__id=case.workflow.id).filter(case__id=None)
        return queryset


class Case(viewsets.ModelViewSet):
    queryset = models.Case.objects.all()
    serializer_class = serializers.Case

    # This logic belongs in workflow.models maybe?
    def perform_create(self, serializer):
        case = serializer.save()
        for stub in case.workflow.parameter_stubs.all():
            if stub.scope == 'CASE':
                parameter = models.Parameter()
                parameter.case = case
                parameter.stub = stub
                parameter.name = stub.name
                parameter.workflow = case.workflow
                parameter.save()
