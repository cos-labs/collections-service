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


from django.http import HttpResponse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework import exceptions as drf_exceptions
from rest_framework import permissions as drf_permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_haystack.viewsets import HaystackViewSet
from guardian.shortcuts import assign_perm

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
    UserSearchSerializer
)
from api.pagination import LargeResultsSetPagination


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

    def get_queryset(self):

        queryset = Collection.objects.all().order_by('-date_created')

        user_id = self.request.query_params.get('user')
        username = self.request.query_params.get('username')
        org_name = self.request.query_params.get("org")

        if user_id:
            queryset = queryset.filter(created_by_id=user_id)
        if username:
            queryset = queryset.filter(created_by__username=username)
        if org_name:
            queryset = queryset.filter(created_by_org=org_name)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        collection = serializer.save()
        assign_perm('api.approve_collection_items', user, collection)
        assign_perm('view', user, collection)

    def retrieve(self, request, *args, **kwargs):
        collection = self.get_object()
        #if request.user.has_perm("view", collection):
            #serializer = self.get_serializer(collection)
            #return Response(serializer.data)
        serializer = self.get_serializer(collection)
        return Response(serializer.data)
        #return HttpResponse('Not Found', status=404)


class ItemViewSet(ModelViewSet):
    """
    # `ItemViewSet`
    """

    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        collection = self.request.data.get('collection')
        if collection:
            queryset = queryset.filter(collection_id=collection)
        return queryset.filter(Q(status='approved') | Q(created_by=user.id) | Q(collection__created_by=user.id))

    def perform_create(self, serializer):
        user = self.request.user
        collection = Collection.objects.get(self.request.data.get("collection"))
        if not user.has_perm('collection.AddItem', collection):
            return HttpResponse('Unauthorized', status=401)
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        #if request.user.has_perm("view", instance):
            #serializer = self.get_serializer(instance)
            #return Response(serializer.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
        #return HttpResponse('Not Found', status=404)


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
