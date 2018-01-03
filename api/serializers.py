# Library Imports
# #############################################################################


import traceback

from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.utils import model_meta
from rest_framework.serializers import (
    ModelSerializer,
    JSONField,
    ChoiceField,
    BooleanField,
    raise_errors_on_nested_writes
)
from rest_framework.relations import (
    ManyRelatedField,
    MANY_RELATION_KWARGS
)
from rest_framework_json_api.serializers import (
    Serializer,
    CharField,
    DateTimeField,
    SerializerMethodField,
    HyperlinkedModelSerializer
)
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user
)

from rest_framework_json_api.relations import (
    ResourceRelatedField
)
from allauth.socialaccount.models import SocialAccount, SocialToken
from drf_haystack.serializers import HaystackSerializer

# App Imports
# #############################################################################


from api.models import (
    Collection,
    Item,
    User,
    ITEM_KINDS,
    ITEM_STATUSES
)


from api import search_indexes


# Model Serializers
# #############################################################################


# class ProtectedManyRelatedField(ManyRelatedField):
#
#     def to_representation(self, iterable):
#         """
#         Override `to_representation` in order to handle filtering of relation
#         by user permissions. The if statement is the change from the original
#         """
#         if type(iterable) == QuerySet:
#             iterable = self.child_relation.get_queryset(iterable)
#         return [
#             self.child_relation.to_representation(value)
#             for value in iterable
#         ]

#
# class ProtectedResourceRelatedField(ResourceRelatedField):
#
#     def get_queryset(self, iterable):
#         user = self.context['request'].user
#         queryset = get_objects_for_user(user, 'view', klass=iterable)
#         return queryset
#
#     @classmethod
#     def many_init(cls, *args, **kwargs):
#         """
#         This method handles creating a parent `ManyRelatedField` instance
#         when the `many=True` keyword argument is passed.
#         Typically you won't need to override this method.
#         Note that we're over-cautious in passing most arguments to both parent
#         and child classes in order to try to cover the general case. If you're
#         overriding this method you'll probably want something much simpler, eg:
#         @classmethod
#         def many_init(cls, *args, **kwargs):
#             kwargs['child'] = cls()
#             return CustomManyRelatedField(*args, **kwargs)
#         """
#         list_kwargs = {'child_relation': cls(*args, **kwargs)}
#         for key in kwargs.keys():
#             if key in MANY_RELATION_KWARGS:
#                 list_kwargs[key] = kwargs[key]
#         return ProtectedManyRelatedField(**list_kwargs)
#

class CollectionModelSerializer(HyperlinkedModelSerializer):
    #
    # def create(self, validated_data):
    #     """
    #     We have a bit of extra checking around this in order to provide
    #     descriptive messages when something goes wrong, but this method is
    #     essentially just:
    #         return ExampleModel.objects.create(**validated_data)
    #     If there are many to many fields present on the instance then they
    #     cannot be set until the model is instantiated, in which case the
    #     implementation is like so:
    #         example_relationship = validated_data.pop('example_relationship')
    #         instance = ExampleModel.objects.create(**validated_data)
    #         instance.example_relationship = example_relationship
    #         return instance
    #     The default implementation also does not handle nested relationships.
    #     If you want to support writable nested relationships you'll need
    #     to write an explicit `.create()` method.
    #     """
    #     raise_errors_on_nested_writes('create', self, validated_data)
    #
    #     ModelClass = self.Meta.model
    #
    #     # Remove many-to-many relationships from validated_data.
    #     # They are not valid arguments to the default `.create()` method,
    #     # as they require that the instance has already been saved.
    #     info = model_meta.get_field_info(ModelClass)
    #     many_to_many = {}
    #     for field_name, relation_info in info.relations.items():
    #         if relation_info.to_many and (field_name in validated_data):
    #             many_to_many[field_name] = validated_data.pop(field_name)
    #
    #     try:
    #         instance = ModelClass.objects.create(**validated_data)
    #     except TypeError:
    #         tb = traceback.format_exc()
    #         msg = (
    #             'Got a `TypeError` when calling `%s.objects.create()`. '
    #             'This may be because you have a writable field on the '
    #             'serializer class that is not a valid argument to '
    #             '`%s.objects.create()`. You may need to make the field '
    #             'read-only, or override the %s.create() method to handle '
    #             'this correctly.\nOriginal exception was:\n %s' %
    #             (
    #                 ModelClass.__name__,
    #                 ModelClass.__name__,
    #                 self.__class__.__name__,
    #                 tb
    #             )
    #         )
    #         raise TypeError(msg)
    #
    #     # Save many-to-many relationships after the instance is created.
    #     if many_to_many:
    #         for field_name, value in many_to_many.items():
    #
    #             # If the m2m has a model defined as a through table, then
    #             # relations cannot be added by that relationship's .add() method,
    #             # but should be created using the model's constructor.
    #             # This loop checks to ensure that if the relation does not exist
    #             # it is created. The way this is set up now, it requires the relation
    #             # to be unique.
    #             if field_name in info.relations and info.relations[field_name].has_through_model:
    #                 field = info.relations[field_name].model_field
    #                 for related_instance in value:
    #                     through_class = field.rel.through
    #                     through_instance = through_class()
    #                     existing_through_instances = through_class.objects\
    #                         .filter(**{field.m2m_field_name()+"_id": instance.id})\
    #                         .filter(**{field.m2m_reverse_field_name()+"_id": related_instance.id})
    #                     if existing_through_instances.exists():
    #                         continue
    #                     setattr(through_instance, field.m2m_field_name(), instance)
    #                     setattr(through_instance, field.m2m_reverse_field_name(), related_instance)
    #                     through_instance.save()
    #
    #             else:
    #                 field = getattr(instance, field_name)
    #                 field.set(value)
    #     return instance
    #
    # def update(self, instance, validated_data):
    #     raise_errors_on_nested_writes('update', self, validated_data)
    #     info = model_meta.get_field_info(instance)
    #
    #     # Simply set each attribute on the instance, and then save it.
    #     # Note that unlike `.create()` we don't need to treat many-to-many
    #     # relationships as being a special case. During updates we already
    #     # have an instance pk for the relationships to be associated with.
    #     for attr, value in validated_data.items():
    #
    #         # If the m2m has a model defined as a through table, then
    #         # relations cannot be added by that relationship's .add() method,
    #         # but should be created using the model's constructor.
    #         # This loop checks to ensure that if the relation does not exist
    #         # it is created. The way this is set up now, it requires the relation
    #         # to be unique.
    #         if attr in info.relations and info.relations[attr].has_through_model:
    #             field = info.relations[attr].model_field
    #             for related_instance in value:
    #                 through_class = field.rel.through
    #                 through_instance = through_class()
    #                 existing_through_instances = through_class.objects\
    #                     .filter(**{field.m2m_field_name()+"_id": instance.id})\
    #                     .filter(**{field.m2m_reverse_field_name()+"_id": related_instance.id})
    #                 if existing_through_instances.exists():
    #                     continue
    #                 setattr(through_instance, field.m2m_field_name(), instance)
    #                 setattr(through_instance, field.m2m_reverse_field_name(), related_instance)
    #                 through_instance.save()
    #
    #         elif attr in info.relations and info.relations[attr].to_many:
    #             field = getattr(instance, attr)
    #             field.set(value)
    #
    #         else:
    #             setattr(instance, attr, value)
    #
    #     instance.save()
    #
    #     return instance
    #
    pass


class CollectionSerializer(CollectionModelSerializer):

    id = CharField(read_only=True)
    title = CharField(required=True)
    description = CharField(required=False, allow_blank=True)
    tags = CharField(required=False, allow_blank=True)
    collection_type = CharField()
    address = CharField(required=False, allow_blank=True, allow_null=True)
    location = CharField(required=False, allow_blank=True, allow_null=True)
    settings = JSONField(required=False)
    submission_settings = JSONField(required=False)
    date_created = DateTimeField(read_only=True)
    date_updated = DateTimeField(read_only=True)
    created_by_org = CharField(allow_blank=True, required=False)
    created_by = ResourceRelatedField(
        queryset=User.objects.all(),
        many=False,
        required=False
    )
    showcased = BooleanField(required=False, default=False)
    can_moderate = SerializerMethodField()
    can_edit = SerializerMethodField()
    can_admin = SerializerMethodField()

    items = ResourceRelatedField(
        many=True,
        required=False,
        read_only=True
    )

    moderators = ResourceRelatedField(
        many=True,
        required=False,
        queryset=User.objects.all()
    )
    admins = ResourceRelatedField(
        many=True,
        required=False,
        queryset=User.objects.all()
    )

    class Meta:
        model = Collection
        fields = [
            'id',
            'title',
            'description',
            'tags',
            'showcased',
            'created_by',
            'location',
            'address',
            'collection_type',
            'settings',
            'created_by_org',
            'submission_settings',
            'date_updated',
            'items',
            'moderators',
            'admins',
            'date_created',
            'can_moderate',
            'can_edit',
            'can_admin'
        ]

    class JSONAPIMeta:
        resource_name = 'collections'

    def get_can_moderate(self, obj):
        user = self.context['request'].user
        return user.has_perm('moderate_collection', obj)

    def get_can_edit(self, obj):
        user = self.context['request'].user
        return user.has_perm('change_collection', obj)

    def get_can_admin(self, obj):
        user = self.context['request'].user
        return user.has_perm('administrate_collection', obj)


class ItemSerializer(CollectionModelSerializer):
    kind = ChoiceField(choices=ITEM_KINDS)
    status = ChoiceField(choices=ITEM_STATUSES)
    created_by = ResourceRelatedField(
        queryset=User.objects.all(),
        many=False,
        required=False
    )
    can_edit = SerializerMethodField()
    date_created = DateTimeField(read_only=True)
    date_submitted = DateTimeField(read_only=True, allow_null=True)
    date_accepted = DateTimeField(read_only=True, allow_null=True)
    collection = ResourceRelatedField(
        queryset=Collection.objects.all(),
        many=False,
        required=True
    )

    class Meta:
        model = Item
        fields = [
            'id',
            'title',
            'kind',
            'description',
            'status',
            'source_id',
            'url',
            'created_by',
            'metadata',
            'date_created',
            'date_submitted',
            'date_accepted',
            'location',
            'start_time',
            'end_time',
            'collection',
            'file_link',
            'file_name',
            'can_edit'
        ]

    class JSONAPIMeta:
        resource_name = 'items'

    def get_can_edit(self, obj):
        user = self.context['request'].user
        return user.has_perm('change_item', obj) or user.has_perm('moderate_collection', obj.collection)


class UserSerializer(CollectionModelSerializer):
    token = SerializerMethodField()

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
            #"collection"
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
            'kind'
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


class GroupSerializer(CollectionModelSerializer):

    name = CharField(required=True)

    class Meta:
        model = Group
        fields = [
            'name'
        ]

