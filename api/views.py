"""
# Collection Views
## Defines
- CollectionViewSet
- ItemViewSet
- ColletionMembershipViweSet
- DocumentviewSet
"""


# Imports
# #############################################################################


import os

from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework import exceptions as drf_exceptions
from rest_framework import permissions as drf_permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_haystack.viewsets import HaystackViewSet
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
)

import requests

import sendgrid
from sendgrid.helpers.mail import *

from api.models import (
    Collection,
    Item,
    User
)
from api.serializers import (
    CollectionSerializer,
    ItemSerializer,
    UserSerializer,
    CollectionSearchSerializer,
    ItemSearchSerializer,
    UserSearchSerializer,
    GroupSerializer

)
from api.pagination import LargeResultsSetPagination
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery

# Views
# #############################################################################


@api_view(['GET'])
def api_root(request):
    return Response({
        'collections': reverse('collection-list', request=request),
        'items': reverse('item-list', request=request)
    })


class CollectionViewSet(ModelViewSet):
    """
    # `CollectionViewSet`
    `ViewSet` for inteacting with Collection models.
    ## `Collection` Attributes
        name           type                description
        =======================================================================
        title          string              group title
        description    string              group description
        date_created   iso8601 timestamp   date/time when the group was created
        date_updated   iso8601 timestamp   date/time when the group was last
                                           updated
    ## Actions
    ### Creating New Groups
        Method:        POST
        URL:           /api/groups
        Query Params:  <none>
        Body (JSON):   {
                         "data": {
                           "type": "groups",                         # required
                           "attributes": {
                             "title":        {title},                # required
                             "description":  {description}           # optional
                           },
                           "relationships": {
                             "collection": {
                               "data": {
                                 "type": "meetings" | "collections"  # required
                                 "id": {collection_id}               # required
                               }
                             }
                           }
                         }
                       }
        Success:       201 CREATED + group representation
    Note: Since the route does not include the collection or meeting id, it
    must be specified in the payload.
    ## This Request/Response
    """

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    # TODO
    # Monkeypatch fields from view so permission logic stays in the view

    #protected_fields = [
    #   "items"
    #]
    #
    #def get_related_items_queryset():
    #    user = self.context['request'].user
    #    queryset = get_objects_for_user(user, 'view', klass=self.queryset)
    #    return queryset
    #
    #def get_serializer(self, *args, **kwargs):
    #    parent = super(ProtectedFieldMixin, self).get_serializer(*args, **kwargs)
    #    for protected_field in self.protected_fields:
    #        if protected_field in parent.fields:
    #            parent.fields[protected_field].queryset = self.filter_queryset(parent.fields[protected_field].queryset)
    #    return parent

    def get_queryset(self):

        user = self.request.user
        query = self.request.query_params.get('q')
        kind = self.request.query_params.get('filter[kind]')
        user_id = self.request.query_params.get('user')
        username = self.request.query_params.get('username')
        org_name = self.request.query_params.get("org")
        showcased = self.request.query_params.get('showcased')

        queryset = Collection.objects.all().order_by('-date_created')

        if showcased:
            queryset = queryset.filter(showcased=True)
        if user_id:
            queryset = queryset.filter(created_by_id=user_id)
        if username:
            queryset = queryset.filter(created_by__username=username)
        if org_name:
            queryset = queryset.filter(created_by_org=org_name)
        if kind:
            queryset = queryset.filter(collection_type=kind)
        if query:
            queryset = queryset.filter(id__in=[instance.pk for instance in SearchQuerySet()\
                .models(Collection)\
                .filter(content=AutoQuery(query))])

        # queryset = get_objects_for_user(user, 'view', klass=queryset)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        collection = serializer.validated_data
        collection["created_by"] = user
        collection = serializer.save()
        assign_perm('change_collection', user, collection)
        assign_perm('moderate_collection', user, collection)
        user.save()

    def retrieve(self, request, *args, **kwargs):
        collection = self.get_object()
        serializer = self.get_serializer(collection)
        return Response(serializer.data)


class ItemViewSet(ModelViewSet):
    """
    # `ItemViewSet`
    """

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):

        user = self.request.user
        user_id = self.request.query_params.get('user')
        username = self.request.query_params.get('username')
        query = self.request.query_params.get("q")
        status = self.request.query_params.get("status")
        collection_id = self.request.query_params.get('collection')

        queryset = self.queryset

        if status:
            queryset = queryset.filter(status=status)
        if user_id:
            queryset = queryset.filter(created_by_id=user_id)
        if username:
            queryset = queryset.filter(created_by__username=username)
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)
        if query:
            queryset = queryset.filter(id__in=[instance.pk for instance in SearchQuerySet()\
                .models(Item)\
                .filter(content=AutoQuery(query))])
        if not user.has_perm('moderate_collection', collection_id):
            queryset.filter(status='approved')

        # queryset = get_objects_for_user(user, 'view', klass=queryset)

        return queryset

    def perform_create(self, serializer):

        user = self.request.user
        item = serializer.validated_data
        collection = item["collection"]

        if item["status"] == "approved" and not user.has_perm('moderate_collection', collection) \
                and collection.moderation_required:
            return HttpResponse('Unauthorized', status=401)
        item = serializer.save(created_by=user)

        assign_perm('change_item', user, item)

        token = user.socialaccount_set.all()[0].socialtoken_set.all()[0].token
        res = requests.get('https://api.osf.io/v2/users/me', headers={
            'authorization': "Bearer " + token,
        })
        recipient_email = res.json()['data']['attributes']['email']

        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        to_email = Email(recipient_email)
        from_email = Email("notifications@osf.io")
        subject = "OSF Collection Submission"
        content = Content("text/plain", "Congratulations on your submission.\n\n" + item.title +
                          " has been created in the collection and is pending approval")
        mail = Mail(from_email, subject, to_email, content)
        sg.client.mail.send.post(request_body=mail.get())

    def perform_update(self, serializer):

        user = self.request.user

        initial_data = serializer.initial_data
        validated_data = serializer.validated_data
        collection = validated_data["collection"]
        if validated_data["status"] != initial_data["status"] and\
                not user.has_perm('moderate_collection', collection):
            return HttpResponse('Unauthorized', status=401)
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # if request.user.has_perm("view", instance):
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
        # serializer = self.get_serializer(instance)
        # return HttpResponse('Not Found', status=404)


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.queryset

    def get_object(self):
        pk = self.kwargs.get("pk")
        if pk == "me":
            return self.request.user
        try:
            return User.objects.get(id=pk)
        except:
            raise drf_exceptions.NotFound


class GroupViewSet(ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializer



# Search Views
# #############################################################################


class CollectionSearchView(HaystackViewSet):
    index_models = [Collection]
    serializer_class = CollectionSearchSerializer


class ItemSearchView(HaystackViewSet):
    index_models = [Item]
    serializer_class = ItemSearchSerializer


class UserSearchView(HaystackViewSet):
    index_models = [User]
    serializer_class = UserSearchSerializer


# EOF
# #############################################################################
