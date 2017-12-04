from rest_framework import permissions
from api.models import Item, Collection

class CanEditCollection(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Collection)
        user = request.user
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        return user.has_perm('api.change_collection', obj)


class CanEditItem(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Item)
        user = request.user
        collection = obj.collection
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        if request.method == 'PATCH':
            return user.id == obj.created_by_id or user.has_perm('api.moderate_collection', collection) \
                or user.has_perm('api.change_item', obj)
        return user.id == obj.created_by_id


class CanViewItem(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Item)
        user = request.user
        # return true if user owns item, is a collection admin, or item is approved
        return user.id == obj.created_by.id \
            or user.has_perm('api.approve_items', obj.collection) \
            or obj.status == 'approved'


class CanModerateCollection(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Item)
        user = request.user
        # return true if user owns the collection or has the permission
        return user.id == obj.created_by.id \
            or user.has_perm('api.approve_items', obj.collection) \
            or obj.status == 'approved'
