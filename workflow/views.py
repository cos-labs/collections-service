
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
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

    def perform_create(self, serializer):
        import ipdb; ipdb.set_trace()

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

    def retrieve(self, request, pk=None):
        case_id = self.request.query_params.get("case")
        parameter_name = self.request.query_params.get("name")
        if not pk:
            try:
                pk = self.queryset.filter(cases__id=case_id)\
                    .get(name=parameter_name).id
                self.kwargs['pk'] = pk
            except MultipleObjectsReturned:
                return Response({"errors": [{
                    "status": "400",
                    "title": "Record not unique",
                    "detail": "The query does not uniquely identify a record;\
                    multiple records were found to match the request. Specify\
                    query parameters that uniquely identify one record, or use\
                    the \"parameter-list\" endpoint."
                }]}, status=400)
            except ObjectDoesNotExist:
                return Response({"errors": [{
                    "status": "404",
                    "title": "Not found",
                    "detail": "No objects were found that match the query."
                }]}, status=404)
        return super().retrieve(request, pk=pk)

    def get_queryset(self):
        queryset = self.queryset
        return queryset


class Case(viewsets.ModelViewSet):
    queryset = models.Case.objects.all()
    serializer_class = serializers.Case

    def get_queryset(self):
        queryset = self.queryset
        collection_id = self.request.query_params.get('collection')
        if collection_id:
            queryset = queryset.filter(collection=collection_id).order_by('-id')
        return queryset

    # This logic belongs in workflow.models maybe?
    def perform_create(self, serializer):
        case = serializer.save()
        if not case.collection:
            case.collection = self.request.query_params.get('collection')
        for stub in case.workflow.parameter_stubs.all():
            case_stub = models.CaseStub()
            case_stub.case = case
            case_stub.stub = stub
            case_stub.save()
            if stub.scope == 'CASE':
                parameter = models.Parameter()
                parameter.stub = stub
                parameter.name = stub.name
                parameter.workflow = case.workflow
                parameter.save()
                case_parameter = models.CaseParameter()
                case_parameter.case = case
                case_parameter.parameter = parameter
                case_parameter.save()
            else:
                parameter = models.Parameter.objects.get(stub=stub)
                case_parameter = models.CaseParameter()
                case_parameter.case = case
                case_parameter.parameter = parameter
                case_parameter.save()
        for section in case.workflow.sections.all():
            section.cases.add(case)
            section.save()
        for widget in case.workflow.widgets.all():
            widget.cases.add(case)
            widget.save()
        for parameter_alias in case.workflow.parameter_aliases.all():
            parameter_alias.cases.add(case)
            parameter_alias.save()
