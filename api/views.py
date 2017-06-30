from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import exceptions as drf_exceptions
from rest_framework import permissions as drf_permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from api.serializers import CollectionSerializer, GroupSerializer, ItemSerializer, UserSerializer
from api.models import Collection, Group, Item, User
from api.permissions import CanEditCollection, CanEditItem, CanEditGroup


@api_view(['GET'])
def api_root(request):
    return Response({
        'collections': reverse('collection-list', request=request),
        'items': reverse('item-list', request=request)
    })


class CollectionList(generics.ListCreateAPIView):
    """View list of collections and create a new collection. """
    serializer_class = CollectionSerializer
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        queryset = Collection.objects.all()
        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        return queryset


class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()
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


class CollectionGroupList(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = (
      drf_permissions.IsAuthenticatedOrReadOnly,
      CanEditGroup
    )

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
        collection = Collection.objects.get(id=collection_id)
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
        collection = Collection.objects.get(id=collection_id)
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