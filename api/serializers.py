from django.utils import timezone
from rest_framework import exceptions
from rest_framework_json_api import serializers
from api.models import Collection, Item, User
from api.base.serializers import RelationshipField
from guardian.shortcuts import assign_perm
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.core.exceptions import ObjectDoesNotExist
from api import search_indexes
from drf_haystack.serializers import HaystackSerializer

from workflow.models import Workflow

from rest_framework_json_api.relations import ResourceRelatedField, SerializerMethodResourceRelatedField

class UserSearchSerializer(HaystackSerializer):

    class Meta:
        index_classes = [search_indexes.UserIndex]
        fields = [
            'text',
            'first_name',
            'last_name',
            'email',
            'full_name'
        ]


class ItemSearchSerializer(HaystackSerializer):

    class Meta:
        index_classes = [search_indexes.ItemIndex]
        fields = [
            'text',
            'title',
            'description',
            'created_by',
            'collection',
            'category'
        ]


class CollectionSearchSerializer(HaystackSerializer):

    class Meta:
        index_classes = [search_indexes.CollectionIndex]
        fields = [
            'text',
            'title',
            'description',
            'created_by'
        ]


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'date_joined',
            'last_login',
            'is_active',
            'gravatar',
            'token'
        ]

    class JSONAPIMeta:
        resource_name = 'users'

    def get_token(self, obj):
        if not obj.id:
            return None
        try:
            account = SocialAccount.objects.get(user=obj)
            token = SocialToken.objects.get(account=account).token
        except ObjectDoesNotExist:
            return None
        return token


class ItemSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=['none', 'project', 'preprint', 'registration', 'presentation', 'website', 'event', 'meeting'])
    status = serializers.ChoiceField(choices=['none', 'approved', 'pending', 'rejected'])
    created_by = UserSerializer(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    date_submitted = serializers.DateTimeField(read_only=True, allow_null=True)
    date_accepted = serializers.DateTimeField(read_only=True, allow_null=True)
    category = serializers.ChoiceField(choices=['none', 'talk', 'poster'], allow_null=True, required=False)

    class Meta:
        model = Item
        fields = (
            'id', 'title', 'type', 'description', 'status', 'source_id', 'url', 'created_by', 'metadata',
            'date_created', 'date_submitted', 'date_accepted', 'location', 'start_time', 'end_time', 'category',
            'file_link'
        )

    class JSONAPIMeta:
        resource_name = 'items'

    def create(self, validated_data):
        user = self.context['request'].user
        collection_id = self.context.get('collection_id', None) or self.context['request'].parser_context['kwargs'].get(
            'pk', None)
        collection = Collection.objects.get(id=collection_id)

        allow_all = None
        if collection.settings:
            allow_all = collection.settings.get('allow_all', None)
        collection_type = collection.collection_type
        if collection_type and validated_data['type'] != collection_type:
            raise ValueError('Collection only accepts items of type ' + collection_type)

        if user.has_perm('api.approve_collection_items', collection) or allow_all:
            status = 'approved'
            validated_data['date_accepted'] = timezone.now()
        else:
            status = 'pending'

        validated_data['status'] = status
        validated_data['date_submitted'] = timezone.now()
        item = Item.objects.create(
            created_by=user,
            collection=collection,
            **validated_data
        )
        return item

    def update(self, item, validated_data):
        user = self.context['request'].user
        status = validated_data.get('status', item.status)
        collection_id = self.context.get('collection_id', None) or self.context['request'].parser_context['kwargs'].get(
            'pk', None)
        if collection_id:
            collection = Collection.objects.get(id=collection_id)
        else:
            collection = item.collection

        if status != item.status and user.has_perm('api.approve_collection_items', collection):
            raise exceptions.PermissionDenied(detail='Cannot change submission status.')
        elif user.id != item.created_by_id and validated_data.keys() != ['status']:
            raise exceptions.PermissionDenied(detail='Cannot update another user\'s submission.')

        item_type = validated_data.get('type', item.type)
        if collection.settings:
            collection_type = collection.settings.get('type', None)
            if collection_type and item_type != collection_type:
                raise ValueError('Collection only accepts items of type ' + collection_type)

        item.source_id = validated_data.get('source_id', item.source_id)
        item.title = validated_data.get('title', item.title)
        item.description = validated_data.get('description', item.description)
        item.type = item_type
        item.status = status
        item.url = validated_data.get('url', item.url)
        item.metadata = validated_data.get('metadata', item.metadata)
        item.location = validated_data.get('location', item.location)
        item.start_time = validated_data.get('start_time', item.start_time)
        item.end_time = validated_data.get('end_time', item.end_time)
        item.category = validated_data.get('category', item.category)
        item.file_link = validated_data.get('file_link', item.file_link)
        item.save()
        return item


class CollectionSerializer(serializers.ModelSerializer):

    included_serializers = {
        'workflow': 'workflow.serializers.Workflow'
    }
    created_by_org = serializers.CharField(allow_blank=True, required=False)
    created_by = RelationshipField(
        related_view='user-detail',
        related_view_kwargs={'user_id': '<created_by.pk>'},
    )
    date_created = serializers.DateTimeField(read_only=True)
    date_updated = serializers.DateTimeField(read_only=True)
    items = RelationshipField(
        related_view='collection-item-list',
        related_view_kwargs={'pk': '<pk>'}
    )

    workflow = ResourceRelatedField(
        queryset=Workflow.objects.all(),
        many=False,
        required=True
    )

    class Meta:
        model = Collection
        fields = (
            'id',
            'title',
            'description',
            'tags',
            'created_by',
            'created_by_org',
            'collection_type',
            'date_created',
            'date_updated',
            'workflow',
            'location',
            'address',
            'items',
            'settings',
            'submission_settings'
        )

    class JSONAPIMeta:
        resource_name = 'collections'
        included_resources = [
            'workflow',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        collection = Collection.objects.create(created_by=user, **validated_data)
        assign_perm('api.approve_collection_items', user, collection)
        return collection

    def update(self, collection, validated_data):
        collection.title = validated_data.get('title', collection.title)
        collection.description = validated_data.get('description', collection.description)
        collection.tags = validated_data.get('tags', collection.tags)
        collection.settings = validated_data.get('settings', collection.settings)
        collection.submission_settings = validated_data.get('submission_settings', collection.submission_settings)
        collection.created_by_org = validated_data.get('created_by_org', collection.created_by_org)
        collection.save()
        return collection
