import json
from django.utils import timezone
from rest_framework import exceptions
from rest_framework_json_api import serializers
from api.models import CollectionBase, Collection, Meeting, Group, Item, User
from api.base.serializers import RelationshipField
from guardian.shortcuts import assign_perm
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.core.exceptions import ObjectDoesNotExist


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login',
            'is_active', 'gravatar', 'token'
        )

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


class ItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=['none', 'project', 'preprint', 'registration', 'presentation', 'website', 'event'])
    status = serializers.ChoiceField(choices=['none', 'approved', 'pending', 'rejected'])
    source_id = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    created_by = UserSerializer(read_only=True)
    metadata = serializers.JSONField(required=False)
    date_created = serializers.DateTimeField(read_only=True)
    date_submitted = serializers.DateTimeField(read_only=True, allow_null=True)
    date_accepted = serializers.DateTimeField(read_only=True, allow_null=True)
    location = serializers.CharField(allow_null=True, required=False)
    start_time = serializers.DateTimeField(allow_null=True, required=False)
    end_time = serializers.DateTimeField(allow_null=True, required=False)
    category = serializers.ChoiceField(choices=['none', 'talk', 'poster'])

    class Meta:
        model = Item

    class JSONAPIMeta:
        resource_name = 'items'

    def create(self, validated_data):
        user = self.context['request'].user
        collection_id = self.context.get('collection_id', None) or self.context['request'].parser_context['kwargs'].get('pk', None)
        collection = CollectionBase.objects.get(id=collection_id)

        allow_all = None
        if collection.settings:
            allow_all = collection.settings.get('allow_all', None)
            collection_type = collection.settings.get('type', None)
            if collection_type and validated_data['type'] != collection_type:
                raise ValueError('Collection only accepts items of type ' + collection_type)

        status = 'pending'
        if user.has_perm(['api.approve_collection_items', 'api.approve_meeting_items'], collection) or allow_all:
            status = 'approved'
            validated_data['date_accepted'] = timezone.now()

        group_id = self.context.get('group_id', None) or self.context['request'].parser_context['kwargs'].get('group_id', None)
        if group_id:
            validated_data['group'] = Group.objects.get(id=group_id)

        validated_data['status'] = status
        validated_data['date_created'] = timezone.now()
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
        collection_id = self.context.get('collection_id', None) or self.context['request'].parser_context['kwargs'].get('pk', None)
        if collection_id:
            collection = CollectionBase.objects.get(id=collection_id)
        else:
            collection = item.collection

        if status != item.status and user.has_perm('api.approve_items', collection):
            raise exceptions.PermissionDenied(detail='Cannot change submission status.')
        elif user.id != item.created_by_id and validated_data.keys() != ['status']:
            raise exceptions.PermissionDenied(detail='Cannot update another user\'s submission.')

        group_id = self.context.get('group_id', None) or self.context['request'].parser_context['kwargs'].get('group_id', None)
        if group_id:
            group = Group.objects.get(id=group_id)
        else:
            group = None

        item_type = validated_data.get('type', item.type)
        if collection.settings:
            collection_type = collection.settings.get('type', None)
            if collection_type and item_type != collection_type:
                raise ValueError('Collection only accepts items of type ' + collection_type)

        item.group = group
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
        item.save()
        return item


class GroupSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(allow_blank=True, required=False)
    created_by = UserSerializer(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    date_updated = serializers.DateTimeField(read_only=True)
    items = RelationshipField(
        related_view='group-item-list',
        related_view_kwargs={'pk': '<collection.id>', 'group_id': '<pk>'}
    )

    class Meta:
        model = Group

    class JSONAPIMeta:
        resource_name = 'groups'

    def create(self, validated_data):
        user = self.context['request'].user
        collection_id = self.context.get('collection_id', None) or self.context['request'].parser_context['kwargs'].get('pk', None)
        collection = CollectionBase.objects.get(id=collection_id)
        return Group.objects.create(
            created_by=user,
            collection=collection,
            **validated_data
        )

    def update(self, group, validated_data):
        group.title = validated_data['title']
        description = validated_data['description']
        if description:
            group.description = description
        group.save()
        return group


class CollectionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.CharField(required=False, allow_blank=True)
    settings = serializers.JSONField(required=False)
    submission_settings = serializers.JSONField(required=False)
    created_by_org = serializers.CharField(allow_blank=True, required=False)
    created_by = RelationshipField(
        related_view='user-detail',
        related_view_kwargs={'user_id': '<created_by.pk>'},
    )
    date_created = serializers.DateTimeField(read_only=True)
    date_updated = serializers.DateTimeField(read_only=True)
    groups = RelationshipField(
        related_view='collection-group-list',
        related_view_kwargs={'pk': '<pk>'}
    )
    items = RelationshipField(
        related_view='collection-item-list',
        related_view_kwargs={'pk': '<pk>'}
    )

    class Meta:
        model = Collection

    class JSONAPIMeta:
        resource_name = 'collections'

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


class MeetingSerializer(CollectionSerializer):
    location = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    address = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    start_date = serializers.DateTimeField(allow_null=True, required=False)
    end_date = serializers.DateTimeField(allow_null=True, required=False)
    groups = RelationshipField(
        related_view='meeting-group-list',
        related_view_kwargs={'pk': '<pk>'}
    )
    items = RelationshipField(
        related_view='meeting-item-list',
        related_view_kwargs={'pk': '<pk>'}
    )

    class Meta:
            model = Meeting

    class JSONAPIMeta:
        resource_name = 'meetings'

    def create(self, validated_data):
        user = self.context['request'].user
        meeting = Meeting.objects.create(created_by=user, **validated_data)
        assign_perm('api.approve_meeting_items', user, CollectionBase(meeting))
        return meeting

    def update(self, meeting, validated_data):
        meeting.title = validated_data.get('title', meeting.title)
        meeting.description = validated_data.get('description', meeting.description)
        meeting.tags = validated_data.get('tags', meeting.tags)
        meeting.settings = validated_data.get('settings', meeting.settings)
        meeting.submission_settings = validated_data.get('submission_settings', meeting.submission_settings)
        meeting.created_by_org = validated_data.get('created_by_org', meeting.created_by_org)
        meeting.location = validated_data.get('location', meeting.location)
        meeting.start_date = validated_data.get('start_date', meeting.start_date)
        meeting.end_date = validated_data.get('end_date', meeting.end_date)
        meeting.save()
        return meeting


class GroupMeetingSerializer(GroupSerializer):
    items = RelationshipField(
        related_view='meeting-group-item-list',
        related_view_kwargs={'pk': '<collection.id>', 'group_id': '<pk>'}
    )