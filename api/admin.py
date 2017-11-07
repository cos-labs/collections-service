from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.admin.helpers import ActionForm
from api.models import Collection, Item
from guardian.shortcuts import get_objects_for_user, assign_perm
from guardian.admin import GuardedModelAdmin

def approve_item(modeladmin, request, queryset):
    queryset.update(status='approved')


def add_admins(modeladmin, request, queryset):
    collection_id = request.POST.get('collection_id')
    collection = Collection.objects.get(id=collection_id)
    for user in queryset:
        # Add permissions to view/change items through django admin
        assign_perm('api.approve_items', user, collection)
        assign_perm('api.change_item', user)
        user.is_staff = True
        user.save()


class AdminForm(ActionForm):
    collection_id = forms.CharField()


class ItemAdmin(GuardedModelAdmin):
    list_display = ('title', 'collection', 'kind', 'created_by', 'status')
    actions = [approve_item]

    def get_search_results(self, request, queryset, search_term):
        user = request.user
        collections = get_objects_for_user(user, 'view_collection', Collection.objects.all())
        can_moderate = list(collections)
        return self.model.objects.filter(collection__in=can_moderate), True

class CollectionAdmin(GuardedModelAdmin):
    list_display = ["title", "collection_type", "description", "created_by", "created_by_org"]

class OSFUserAdmin(UserAdmin):
    model = get_user_model()
    action_form = AdminForm
    actions = [add_admins]


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(get_user_model(), OSFUserAdmin)

admin.site.register(Permission)
