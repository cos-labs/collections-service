from rest_framework import permissions
from api.models import Collection, Group, Item


class CanEditCollection(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Collection)
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by is user


class CanEditGroup(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Group)
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by is user


class CanEditItem(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Item)
        user = request.user
        collection = obj.collection
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == 'PATCH':
            return user.id == obj.created_by_id or user.has_perm('api.approve_items', collection)
        return user.id == obj.created_by_id
