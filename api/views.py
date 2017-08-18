from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import exceptions as drf_exceptions
from rest_framework import permissions as drf_permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from api.serializers import CollectionSerializer, CollectionSearchSerializer, MeetingSerializer, \
    MeetingSearchSerializer, GroupSerializer,GroupMeetingSerializer, ItemSerializer, ItemSearchSerializer, \
    CollectionBaseSearchSerializer, UserSerializer, UserSearchSerializer
from api.models import CollectionBase, Collection, Meeting, Group, Item, User
from api.permissions import CanEditCollection, CanEditItem, CanEditGroup

from drf_haystack.viewsets import HaystackViewSet


class CollectionSearchView(HaystackViewSet):
    index_models = [Collection]
    serializer_class = CollectionSearchSerializer


class CollectionBaseSearchView(HaystackViewSet):
    index_models = [CollectionBase]
    serializer_class = CollectionBaseSearchSerializer


class MeetingSearchView(HaystackViewSet):
    index_models = [Meeting]
    serializer_class = MeetingSearchSerializer


class ItemSearchView(HaystackViewSet):
    index_models = [Item]
    serializer_class = ItemSearchSerializer


class UserSearchView(HaystackViewSet):
    index_models = [User]
    serializer_class = UserSearchSerializer


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
                               "type": "collections",                         # required
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
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly,)

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
                                 "title":               {title},              # required
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
    """ View list of meetings and create a new meeting.

    ## Meeting Attributes

        name                          type                    description
        =================================================================================================================
        title                         string                  meeting title
        description                   string                  meeting description
        tags                          string                  tags describing the meeting
        settings                      object                  general settings for the meeting (e.g. collection_type)
        submission_settings           object                  settings for the meeting's submission form
        created_by_org                string                  the organization/institution associated with the meeting
        date_created                  iso8601 timestamp       date/time when the meeting was created
        date_updated                  iso8601 timestamp       date/time when the meeting was last updated
        location                      string                  location of the meeting
        address                       string                  street address of the meeting location
        start_date                    iso8601 timestamp       date/time when the meeting begins
        end_date                      iso8601 timestamp       date/time when the meeting ends

    ## Actions

    ### Creating New Meetings

            Method:        POST
            URL:           /api/meetings
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "meetings",                            # required
                               "attributes": {
                                 "title":               {title},              # required
                                 "description":         {description},        # optional
                                 "tags":                {tag1, tag2, },       # optional
                                 "created_by_org":      {created_by_org}      # optional
                                 "settings":            {settings}            # optional
                                 "submission_settings": {submission_settings} # optional
                                 "location":            {location}            # optional
                                 "address":             {address}             # optional
                                 "start_date":          {start_date}          # optional
                                 "end_date":            {end_date}            # optional
                               }
                             }
                           }
            Success:       201 CREATED + meeting representation

    ## Query Params
    +  `title=<Str>`: filters meetings by title

    #This Request/Response

    """
    serializer_class = MeetingSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Meeting.objects.all()
        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        return queryset


class MeetingDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Details about a given meeting.

     ## Meeting Attributes

        name                          type                    description
        =================================================================================================================
        title                         string                  meeting title
        description                   string                  meeting description
        tags                          string                  tags describing the meeting
        settings                      object                  general settings for the meeting (e.g. collection_type)
        submission_settings           object                  settings for the meeting's submission form
        created_by_org                string                  the organization/institution associated with the meeting
        date_created                  iso8601 timestamp       date/time when the meeting was created
        date_updated                  iso8601 timestamp       date/time when the meeting was last updated
        location                      string                  location of the meeting
        address                       string                  street address of the meeting location
        start_date                    iso8601 timestamp       date/time when the meeting begins
        end_date                      iso8601 timestamp       date/time when the meeting ends

    ##Relationships

    ### Groups

    List of groups that belong to this meeting.

    ### Items

    List of top-level items that belong to this meeting.

    ### Created By

    User who created this meeting.

    ## Actions

    ###Update

            Method:        PUT / PATCH
            URL:           /api/meeting/<meeting_id>
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "meetings",                            # required
                               "id":   {meeting_id},                          # required
                               "attributes": {
                                 "title":               {title},              # required for PUT
                                 "description":         {description},        # optional
                                 "tags":                {tag1, tag2, },       # optional
                                 "created_by_org":      {created_by_org}      # optional
                                 "settings":            {settings}            # optional
                                 "submission_settings": {submission_settings} # optional
                                 "location":            {location}            # optional
                                 "address":             {address}             # optional
                                 "start_date":          {start_date}          # optional
                                 "end_date":            {end_date}            # optional
                               }
                             }
                           }
            Success:       200 OK + meeting representation

    Note: The `title` is required with PUT requests and optional with PATCH requests.

    ###Delete
            Method:   DELETE
            URL:      /api/meetings/<meeting_id>
            Params:   <none>
            Success:  204 No Content

    #This Request/Response
    """

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
    """ View list of groups in a given collection/meeting, or create a new group in a given collection/meeting.

    ## Group Attributes

        name                          type                    description
        =================================================================================================================
        title                         string                  group title
        description                   string                  group description
        date_created                  iso8601 timestamp       date/time when the group was created
        date_updated                  iso8601 timestamp       date/time when the group was last updated

    ## Actions

    ### Creating New Groups

            Method:        POST
            URL:           /api/collections/<collection_id>/groups OR /api/meetings/<meeting_id>/groups
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "groups",                 # required
                               "attributes": {
                                 "title":        {title},        # required
                                 "description":  {description},  # optional
                               }
                             }
                           }
            Success:       201 CREATED + group representation

    #This Request/Response

    """
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
    """ View list of all groups, or create a new group in a collection or meeting.

    ## Group Attributes

        name                          type                    description
        =================================================================================================================
        title                         string                  group title
        description                   string                  group description
        date_created                  iso8601 timestamp       date/time when the group was created
        date_updated                  iso8601 timestamp       date/time when the group was last updated

    ## Actions

    ### Creating New Groups

            Method:        POST
            URL:           /api/groups
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "groups",                          # required
                               "attributes": {
                                 "title":        {title},                 # required
                                 "description":  {description}            # optional
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

    Note: Since the route does not include the collection or meeting id, it must be specified in the payload.

    #This Request/Response

    """
    serializer_class = GroupSerializer
    permission_classes = (
        drf_permissions.IsAuthenticatedOrReadOnly,
        CanEditGroup
    )

    def get_serializer_context(self):
        context = super(GroupList, self).get_serializer_context()
        collection = self.request.data.get('collection', None)
        if collection:
            context.update({'collection_id': collection['id']})
        return context

    def get_queryset(self):
        return Group.objects.all()


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Details about a given group.

    ## Group Attributes

        name                          type                    description
        =================================================================================================================
        title                         string                  group title
        description                   string                  group description
        date_created                  iso8601 timestamp       date/time when the group was created
        date_updated                  iso8601 timestamp       date/time when the group was last updated

    ##Relationships

    ### Items

    List of items that belong to this group.

    ### Created By

    User who created this group.

    ## Actions

    ###Update

            Method:        PUT / PATCH
            URL:           /api/collections/<collection_id>/groups/<group_id> OR
                           /api/meetings/<meeting_id>/groups/<group_id> OR
                           /api/groups/<group_id>
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "groups",                            # required
                               "id":   {group_id},                          # required
                               "attributes": {
                                 "title":               {title},            # required
                                 "description":         {description}       # optional
                               }
                             }
                           }
            Success:       200 OK + group representation

    Note: The `title` is required with PUT requests and optional with PATCH requests.

    ###Delete
            Method:   DELETE
            URL:      /api/collections/<collection_id>/groups/<group_id> OR
                      /api/meetings/<meeting_id>/groups/<group_id> OR
                      /api/groups/<group_id>
            Params:   <none>
            Success:  204 No Content

    #This Request/Response

    """
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
    """ View list of items in a given collection/meeting, or create a new item in a given collection/meeting.

    ## Item Attributes

        name                          type                    description
        ================================================================================================================
        title                         string                  item title
        description                   string                  item description
        type                          string                  type of item (e.g. 'project', 'presentation', etc.)
        status                        string                  moderation status ('approved', 'pending', 'rejected')
        source_id                     string                  guid of associated OSF object (e.g. node_id for an OSF project)
        url                           string                  url of associated OSF object (e.g. project url)
        metadata                      object                  additional information about the item
        date_created                  iso8601 timestamp       date/time when the item was created
        date_submitted                iso8601 timestamp       date/time when the item was submitted
        date_accepted                 iso8601 timestamp       date/time when the item was accepted
        location                      string                  location of the event item
        start_time                    iso8601 timestamp       date/time when the event item begins
        end_time                      iso8601 timestamp       date/time when the event item ends
        category                      string                  item category (e.g. 'talk', 'poster')

    ## Actions

    ### Creating New Items

            Method:        POST
            URL:           /api/collections/<collection_id>/items OR /api/meetings/<meeting_id>/items
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "items",                  # required
                               "attributes": {
                                 "title":       {title},         # required
                                 "description": {description},   # optional
                                 "type":        {type},          # required
                                 "status":      {status},        # required
                                 "source_id":   {source_id},     # optional
                                 "url":         {url},           # optional
                                 "metadata":    {metadata},      # optional
                                 "location":    {location},      # optional
                                 "start_time":  {start_time},    # optional
                                 "end_time":    {end_time},      # optional
                                 "category":    {category}       # required
                               }
                             }
                           }
            Success:       201 CREATED + item representation

    Note: Items added by the collection creator will automatically have the status "approved". If "approve_all" is true
    in collection.settings, items added by other users will automatically have the status "approved", otherwise
    they will be "pending".

    #This Request/Response
    """
    serializer_class = ItemSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        collection_id = self.kwargs['pk']
        collection = CollectionBase.objects.get(id=collection_id)
        queryset = Item.objects.filter(collection=collection_id, group=None)
        if user.id == collection.created_by_id:
            return queryset
        return queryset.filter(Q(status='approved') | Q(created_by=user.id))


class GroupItemList(generics.ListCreateAPIView):
    """ View list of items or create a new item in a given group.

    ## Item Attributes

        name                          type                    description
        ================================================================================================================
        title                         string                  item title
        description                   string                  item description
        type                          string                  type of item (e.g. 'project', 'presentation', etc.)
        status                        string                  moderation status ('approved', 'pending', 'rejected')
        source_id                     string                  guid of associated OSF object (e.g. node_id for an OSF project)
        url                           string                  url of associated OSF object (e.g. project url)
        metadata                      object                  additional information about the item
        date_created                  iso8601 timestamp       date/time when the item was created
        date_submitted                iso8601 timestamp       date/time when the item was submitted
        date_accepted                 iso8601 timestamp       date/time when the item was accepted
        location                      string                  location of the event item
        start_time                    iso8601 timestamp       date/time when the event item begins
        end_time                      iso8601 timestamp       date/time when the event item ends
        category                      string                  item category (e.g. 'talk', 'poster')

    ## Actions

    ### Creating New Items

            Method:        POST
            URL:           /api/collections/<collection_id>/groups/<group_id>/items OR
                           /api/meetings/<meeting_id>/groups/<group_id>/items
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "items",                  # required
                               "attributes": {
                                 "title":       {title},         # required
                                 "description": {description},   # optional
                                 "type":        {type},          # required
                                 "status":      {status},        # required
                                 "source_id":   {source_id},     # optional
                                 "url":         {url},           # optional
                                 "metadata":    {metadata},      # optional
                                 "location":    {location},      # optional
                                 "start_time":  {start_time},    # optional
                                 "end_time":    {end_time},      # optional
                                 "category":    {category}       # required
                               }
                             }
                           }
            Success:       201 CREATED + item representation

    Note: Items added by the collection creator will automatically have the status "approved". If "approve_all" is true
    in collection.settings, items added by other users will automatically have the status "approved", otherwise
    they will be "pending".

    #This Request/Response
    """

    serializer_class = ItemSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        collection_id = self.kwargs['pk']
        collection = CollectionBase.objects.get(id=collection_id)
        queryset = Item.objects.filter(group=self.kwargs['group_id'])
        if user.id == collection.created_by_id:
            return queryset
        return queryset.filter(Q(status='approved') | Q(created_by=user.id))


class ItemList(generics.ListCreateAPIView):
    """ View list of all items, or create a new item in a collection/meeting or group.

    ## Item Attributes

        name                          type                    description
        ================================================================================================================
        title                         string                  item title
        description                   string                  item description
        type                          string                  type of item (e.g. 'project', 'presentation', etc.)
        status                        string                  moderation status ('approved', 'pending', 'rejected')
        source_id                     string                  guid of associated OSF object (e.g. node_id for an OSF project)
        url                           string                  url of associated OSF object (e.g. project url)
        metadata                      object                  additional information about the item
        date_created                  iso8601 timestamp       date/time when the item was created
        date_submitted                iso8601 timestamp       date/time when the item was submitted
        date_accepted                 iso8601 timestamp       date/time when the item was accepted
        location                      string                  location of the event item
        start_time                    iso8601 timestamp       date/time when the event item begins
        end_time                      iso8601 timestamp       date/time when the event item ends
        category                      string                  item category (e.g. 'talk', 'poster')

    ## Actions

    ### Creating New Items

            Method:        POST
            URL:           /api/items
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "items",                  # required
                               "attributes": {
                                 "title":       {title},         # required
                                 "description": {description},   # optional
                                 "type":        {type},          # required
                                 "status":      {status},        # required
                                 "source_id":   {source_id},     # optional
                                 "url":         {url},           # optional
                                 "metadata":    {metadata},      # optional
                                 "location":    {location},      # optional
                                 "start_time":  {start_time},    # optional
                                 "end_time":    {end_time},      # optional
                                 "category":    {category}       # required
                               },
                               "relationships": {
                                 "collection": {
                                    "data": {
                                      "type": "meetings" | "collections"  # required
                                      "id": {collection_id}               # required
                                    }
                                 },
                                 "group": {
                                   "data": {
                                     "type": "groups",                    # optional
                                     "id": {group_id}                     # optional
                                   }
                                 }
                               }
                             }
                           }
            Success:       201 CREATED + item representation


    ### Notes:
    - Since the route does not include the collection/meeting id or a group id, they must be specified in the payload.

    - Items added by the collection creator will automatically have the status "approved". If "approve_all" is true
    in collection.settings, items added by other users will automatically have the status "approved", otherwise
    they will be "pending".

    """
    serializer_class = ItemSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly,)

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
    """ Details for a given item.

    ## Item Attributes

        name                          type                    description
        ================================================================================================================
        title                         string                  item title
        description                   string                  item description
        type                          string                  type of item (e.g. 'project', 'presentation', etc.)
        status                        string                  moderation status ('approved', 'pending', 'rejected')
        source_id                     string                  guid of associated OSF object (e.g. node_id for an OSF project)
        url                           string                  url of associated OSF object (e.g. project url)
        metadata                      object                  additional information about the item
        date_created                  iso8601 timestamp       date/time when the item was created
        date_submitted                iso8601 timestamp       date/time when the item was submitted
        date_accepted                 iso8601 timestamp       date/time when the item was accepted
        location                      string                  location of the event item
        start_time                    iso8601 timestamp       date/time when the event item begins
        end_time                      iso8601 timestamp       date/time when the event item ends
        category                      string                  item category (e.g. 'talk', 'poster')

    ##Relationships

    ### Created By

    User who created this item.

    ## Actions

    ###Update

            Method:        PUT / PATCH
            URL:           /api/collections/<collection_id>/groups/<group_id>/items/<item_id> OR
                           /api/meetings/<meeting_id>/groups/<group_id>/items/<item_id> OR
                           /api/items/<item_id>
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "items",                  # required
                               "attributes": {
                                 "title":       {title},         # required
                                 "description": {description},   # optional
                                 "type":        {type},          # required
                                 "status":      {status},        # required
                                 "source_id":   {source_id},     # optional
                                 "url":         {url},           # optional
                                 "metadata":    {metadata},      # optional
                                 "location":    {location},      # optional
                                 "start_time":  {start_time},    # optional
                                 "end_time":    {end_time},      # optional
                                 "category":    {category}       # required
                               }
                             }
                           }
            Success:       200 OK + item representation

    Note: The `title`, `type`, `status` and `category` fields are required for PUT and optional for PATCH requests.

    ###Delete
            Method:   DELETE
            URL:      /api/collections/<collection_id>/groups/<group_id>/items/<item_id> OR
                      /api/meetings/<meeting_id>/groups/<group_id>/items/<item_id> OR
                      /api/items/<item_id>
            Params:   <none>
            Success:  204 No Content

    #This Request/Response

    """
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
    """ Details about the currently logged-in user.

    ## User Attributes

        name                          type                    description
        ======================================================================================================
        username                      string                  username for the user
        first_name                    string                  first name of the user
        last_name                     string                  last name of the user
        email                         string                  email address associated with the user's account
        date_joined                   iso8601 timestamp       date/time of account creation
        last_login                    iso8601 timestamp       date/time of last login
        is_active                     boolean                 whether the user account is active
        gravatar                      string                  link to user gravatar
        token                         string                  access token for social account (used for OAUTH)

    ## Actions

    ###Update

            Method:        PUT / PATCH
            URL:           /api/users/<user_id>
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "users",                       # required
                               "id":   {user_id},                     # required
                               "attributes": {
                                 "username":       {username},        # required
                                 "first_name":     {first_name},      # optional
                                 "last_name":      {last_name},       # optional
                                 "email":          {email}            # optional
                                 "date_joined":    {date_joined}      # optional
                                 "last_login":     {last_login}       # optional
                                 "is_active":      {is_active}        # optional
                                 "gravatar":       {gravatar}         # optional
                               }
                             }
                           }
            Success:       200 OK + user representation

    ###Delete
            Method:   DELETE
            URL:      /api/users/<user_id>
            Params:   <none>
            Success:  204 No Content

    #This Request/Response

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserList(generics.ListAPIView):
    """ View list of users.

    ## User Attributes

        name                          type                    description
        ======================================================================================================
        username                      string                  username for the user
        first_name                    string                  first name of the user
        last_name                     string                  last name of the user
        email                         string                  email address associated with the user's account
        date_joined                   iso8601 timestamp       date/time of account creation
        last_login                    iso8601 timestamp       date/time of last login
        is_active                     boolean                 whether the user account is active
        gravatar                      string                  link to user gravatar
        token                         string                  access token for social account (used for OAUTH)

    #This Request/Response

    """
    serializer_class = UserSerializer

    # permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        return User.objects.all()


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Details about a given user.

    ## User Attributes

        name                          type                    description
        ======================================================================================================
        username                      string                  username for the user
        first_name                    string                  first name of the user
        last_name                     string                  last name of the user
        email                         string                  email address associated with the user's account
        date_joined                   iso8601 timestamp       date/time of account creation
        last_login                    iso8601 timestamp       date/time of last login
        is_active                     boolean                 whether the user account is active
        gravatar                      string                  link to user gravatar
        token                         string                  access token for social account (used for OAUTH)

    ## Actions

    ###Update

            Method:        PUT / PATCH
            URL:           /api/users/<user_id>
            Query Params:  <none>
            Body (JSON):   {
                             "data": {
                               "type": "users",                       # required
                               "id":   {user_id},                     # required
                               "attributes": {
                                 "username":       {username},        # required
                                 "first_name":     {first_name},      # optional
                                 "last_name":      {last_name},       # optional
                                 "email":          {email}            # optional
                                 "date_joined":    {date_joined}      # optional
                                 "last_login":     {last_login}       # optional
                                 "is_active":      {is_active}        # optional
                                 "gravatar":       {gravatar}         # optional
                               }
                             }
                           }
            Success:       200 OK + user representation

    ###Delete
            Method:   DELETE
            URL:      /api/users/<user_id>
            Params:   <none>
            Success:  204 No Content

    #This Request/Response
    """
    serializer_class = UserSerializer

    # permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_object(self):
        try:
            user = User.objects.get(id=self.kwargs['user_id'])
        except ObjectDoesNotExist:
            raise drf_exceptions.NotFound
        return user
