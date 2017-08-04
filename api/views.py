from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import exceptions as drf_exceptions
from rest_framework import permissions as drf_permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from api.serializers import CollectionSerializer, MeetingSerializer, GroupSerializer, GroupMeetingSerializer, ItemSerializer, UserSerializer
from api.models import CollectionBase, Collection, Meeting, Group, Item, User
from api.permissions import CanEditCollection, CanEditItem, CanEditGroup


@api_view(['GET'])
def api_root(request):
    return Response({
        'collections': reverse('collection-list', request=request),
        'items': reverse('item-list', request=request)
    })


class CollectionList(generics.ListCreateAPIView):
    """ View list of collections and create a new collection.

    ## Collection Attributes

        name                          type                    description
        =================================================================================================================
        title                         string                  collection title
        description                   string                  collection description
        tags                          string                  tags describing the collection
        settings                      object                  general settings for the collection (e.g. collection_type)
        submission_settings           object                  settings for the collection's submission form
        created_by_org                string                  the organization/institution associated with the collection
        date_created                  iso8601 timestamp       date/time when the collection was created
        date_updated                  iso8601 timestamp       date/time when the collection was last updated

    ## Actions

    ### Creating New Collections

            Method:        POST
            URL:           /api/collections
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "collections", # required
                               "attributes": {
                                 "title":               {title},              # required
                                 "description":         {description},        # optional
                                 "tags":                {tag1, tag2, },       # optional
                                 "created_by_org":      {created_by_org}      # optional
                                 "settings":            {settings}            # optional
                                 "submission_settings": {submission_settings} # optional
                               }
                             }
                           }
            Success:       201 CREATED + collection representation

    ## Query Params
    +  `title=<Str>`: filters collections by title

    #This Request/Response

    """
    serializer_class = CollectionSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        queryset = Collection.objects.all()
        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        return queryset


class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Details about a given collection.

    ## Collection Attributes

        name                          type                    description
        =================================================================================================================
        title                         string                  collection title
        description                   string                  collection description
        tags                          string                  tags describing the collection
        settings                      object                  general settings for the collection (e.g. collection_type)
        submission_settings           object                  settings for the collection's submission form
        created_by_org                string                  the organization/institution associated with the collection
        date_created                  iso8601 timestamp       date/time when the collection was created
        date_updated                  iso8601 timestamp       date/time when the collection was last updated

    ##Relationships

    ### Groups

    List of groups that belong to this collection.

    ### Items

    List of top-level items that belong to this collection.

    ### Created By

    User who created this collection.

    ## Actions

    ###Update

            Method:        PUT / PATCH
            URL:           /api/collections/<collection_id>
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "collections",   # required
                               "id":   {collection_id}, # required
                               "attributes": {
                                 "title":               {title},              # required for PUT
                                 "description":         {description},        # optional
                                 "tags":                {tag1, tag2, },       # optional
                                 "created_by_org":      {created_by_org}      # optional
                                 "settings":            {settings}            # optional
                                 "submission_settings": {submission_settings} # optional
                               }
                             }
                           }
            Success:       200 OK + collection representation

    Note: The `title` is required with PUT requests and optional with PATCH requests.

    ###Delete
            Method:   DELETE
            URL:      /api/collections/<collection_id>
            Params:   <none>
            Success:  204 No Content

    #This Request/Response

    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = (
      drf_permissions.IsAuthenticatedOrReadOnly,
      CanEditCollection
    )

    def get_object(self):
        try:
            collection = Collection.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise drf_exceptions.NotFound
        return collection


class MeetingList(generics.ListCreateAPIView):
    """View list of collections and create a new collection. """
    serializer_class = MeetingSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        queryset = Meeting.objects.all()
        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        return queryset


class MeetingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = (
      drf_permissions.IsAuthenticatedOrReadOnly,
      CanEditCollection
    )

    def get_object(self):
        try:
            collection = Meeting.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise drf_exceptions.NotFound
        return collection


class CollectionGroupList(generics.ListCreateAPIView):
    permission_classes = (
      drf_permissions.IsAuthenticatedOrReadOnly,
      CanEditGroup
    )

    def get_serializer_class(self):
        collection = CollectionBase.objects.get(id=self.kwargs['pk'])
        if collection.type == 'api.meeting':
            return GroupMeetingSerializer
        else:
            return GroupSerializer

    def get_queryset(self):
        return Group.objects.filter(collection=self.kwargs['pk'])


class GroupList(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = (
      drf_permissions.IsAuthenticatedOrReadOnly,
      CanEditGroup
    )

    def get_serializer_context(self):
        context = super(GroupList, self).get_serializer_context()
        collection = self.request.data.get('collection', None)
        context.update({'collection_id': collection['id']})
        return context

    def get_queryset(self):
        return Group.objects.all()


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = (
      drf_permissions.IsAuthenticatedOrReadOnly,
      CanEditGroup
    )

    def get_object(self):
        try:
            group = Group.objects.get(id=self.kwargs['group_id'])
        except ObjectDoesNotExist:
            raise drf_exceptions.NotFound
        return group


class CollectionItemList(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        user = self.request.user
        collection_id = self.kwargs['pk']
        collection = CollectionBase.objects.get(id=collection_id)
        queryset = Item.objects.filter(collection=collection_id, group=None)
        if user.id == collection.created_by_id:
            return queryset
        return queryset.filter(Q(status='approved') | Q(created_by=user.id))


class GroupItemList(generics.ListCreateAPIView):
    """View items in a collection and create a new item to add to the collection. """
    serializer_class = ItemSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        user = self.request.user
        collection_id = self.kwargs['pk']
        collection = CollectionBase.objects.get(id=collection_id)
        queryset = Item.objects.filter(group=self.kwargs['group_id'])
        if user.id == collection.created_by_id:
            return queryset
        return queryset.filter(Q(status='approved') | Q(created_by=user.id))


class ItemList(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_serializer_context(self):
        context = super(ItemList, self).get_serializer_context()
        collection = self.request.data.get('collection', None)
        if collection:
            context.update({'collection_id': collection['id']})
        group = self.request.data.get('group', None)
        if group:
            context.update({'group_id': group['id']})
        return context

    def get_queryset(self):
        user = self.request.user
        return Item.objects.filter(Q(status='approved') | Q(created_by=user.id) | Q(collection__created_by=user.id))


class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    permission_classes = (
      drf_permissions.IsAuthenticatedOrReadOnly,
      CanEditItem
    )

    def get_serializer_context(self):
        context = super(ItemDetail, self).get_serializer_context()
        collection = self.request.data.get('collection', None)
        if collection:
            context.update({'collection_id': collection['id']})
        group = self.request.data.get('group', None)
        if group:
            context.update({'group_id': group['id']})
        else:
            context.update({'group_id': None})

        return context

    def get_object(self):
        try:
            item = Item.objects.get(id=self.kwargs['item_id'])
        except ObjectDoesNotExist:
            raise drf_exceptions.NotFound
        return item


class CurrentUser(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserList(generics.ListAPIView):
    """View list of users. """
    serializer_class = UserSerializer
    # permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return User.objects.all()


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """View user detail. """
    serializer_class = UserSerializer
    # permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_object(self):
        try:
            user = User.objects.get(id=self.kwargs['user_id'])
        except ObjectDoesNotExist:
            raise drf_exceptions.NotFound
        return user
