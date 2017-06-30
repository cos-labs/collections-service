from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.helpers import ActionForm
from api.models import Collection, Group, Item
from guardian.shortcuts import get_objects_for_user, assign_perm


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


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'collection')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'collection', 'type', 'created_by', 'status')
    actions = [approve_item]

    def get_search_results(self, request, queryset, search_term):
        user = request.user
        collections = get_objects_for_user(user, 'api.approve_items')
        return self.model.objects.filter(collection__in=collections), True


class OSFUserAdmin(UserAdmin):
    model = get_user_model()
    action_form = AdminForm
    actions = [add_admins]


admin.site.register(Collection)
admin.site.register(Group, GroupAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(get_user_model(), OSFUserAdmin)
