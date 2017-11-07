from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    Group
)
from django.contrib.postgres.fields import JSONField
from guardian.mixins import GuardianUserMixin

from tests import resources

import datetime


ITEM_KINDS = [
    ('none', 'none'),
    ('project', 'project'),
    ('preprint', 'preprint'),
    ('registration', 'registration'),
    ('presentation', 'presentation'),
    ("repository", "repository"),
    ('website', 'website'),
    ('event', 'event'),
    ('meeting', 'meeting'),
    ("talk", "talk"),
    ("poster", "poster")
]

ITEM_STATUSES = [
    ('none', 'none'),
    ('approved', 'approved'),
    ('pending', 'pending'),
    ('rejected', 'rejected'),
    ("pending/visible", "pending/visible"),
    ("pending/hidden", "pending/hidden")
]


class User(AbstractUser, GuardianUserMixin):
    id = models.AutoField(primary_key=True)
    gravatar = models.URLField(blank=True, null=True)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def save(self, *args, **kwargs):
        try:
            public_group = Group.objects.get(name="public")
        except:
            public_group = Group()
            public_group.name = "public"
            public_group.save()
        if not self.pk:
            super().save(*args, **kwargs)
            self.groups.add(public_group)
            self.save()

def get_anonymous_user_instance(User):
    return User(username="anonymous")


class Collection(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    created_by_org = models.CharField(null=True, blank=True, max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    settings = JSONField(default={}, blank=True, null=True)
    submission_settings = JSONField(default={}, blank=True, null=True)
    collection_type = models.CharField(max_length=50)
    location = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User)

    admins = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        related_name="collection"
    )

    groups = models.ManyToManyField(
        "CollectionGroup",
        blank=True,
        related_name="authorized_collection_workflows"
    )

    workflows = models.ManyToManyField(
        "workflow.Workflow",
        related_name="collections",
        through='CollectionWorkflow'
    )


    def save(self, *args, **kwargs):

        if not self.pk:  # If this is the first save

            if self.collection_type == 'meeting':
                self.settings = resources.meeting_json
            elif self.collection_type == 'repository':
                self.settings = resources.repository_json

            super().save(*args, **kwargs)

            if not getattr(self, "admins", None):
                admin_group = Group()
                admin_group.name = self.title + "("+str(self.id)+")" + " Admin Group"
                admin_group.save(force_insert=True)
                self.admins = admin_group
                self.save(force_update=True)

        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ("view_collection", "View this collection"),
            ("add_item", "Add a item to the collection")
        )


class CollectionGroup(models.Model):

    role = models.TextField(null=True, blank=True)

    collection = models.ForeignKey(
        "Collection",
        null=False,
        blank=False,
        related_name="collection_groups",
    )

    group = models.ForeignKey(
        Group,
        null=False,
        blank=False,
        related_name="collection_groups"
    )

    def __str__(self):
        return self.collection.name + self.role

    class Meta:
        permissions = (
            ("write", "Write priviledges"),
        )


class CollectionWorkflow(models.Model):

    role = models.TextField(null=True, blank=True)

    collection = models.ForeignKey(
        'Collection',
        related_name="collection_workflows"
    )

    workflow = models.ForeignKey(
        'workflow.Workflow',
        null=True,
        blank=True,
        related_name="collection_workflows",
        on_delete=models.SET_NULL
    )

    authorized_groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="authorized_collection_workflows"
    )

    def __str__(self):
        return self.collection.name + self.workflow.title

    class Meta:
        permissions = (
            ("write", "Write priviledges"),
        )


class Item(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    kind = models.CharField(choices=ITEM_KINDS, max_length=200)
    status = models.CharField(choices=ITEM_STATUSES, null=True, max_length=200)
    source_id = models.CharField(null=True, blank=True, max_length=200)
    url = models.URLField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateTimeField(null=True, blank=True, default=None)
    date_accepted = models.DateTimeField(null=True, blank=True, default=None)
    location = models.CharField(null=True, blank=True, default=None, max_length=200)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    file_link = models.CharField(null=True, blank=True, max_length=1000)
    file_name = models.CharField(null=True, blank=True, max_length=1000)

    collection = models.ForeignKey('Collection', related_name='items')
    created_by = models.ForeignKey(User)

    class Meta:
        permissions = (
            ("edit", "Edit this item"),
            ("view", "View this item"),
            ("approve", "Approve this item")
        )
