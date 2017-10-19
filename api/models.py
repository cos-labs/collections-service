from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    Group
)
from django.contrib.postgres.fields import JSONField
from tests import resources


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    gravatar = models.URLField(blank=True)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def save(self, *args, **kwargs):
        try:
            public_group = Group.objects.get(pk=1)
        except:
            public_group = Group()
            public_group.pk = 1
            public_group.name = "public"
            public_group.save()
        self.groups.add(public_group)
        super().save(*args, **kwargs)


class Collection(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User)
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

    workflow = models.ForeignKey(
        'workflow.Workflow',
        null=True,
        blank=True,
        related_name="collections",
        on_delete=models.SET_NULL
    )

    def save(self, *args, **kwargs):
        if not self.pk:  # if this is the first save, set default settings based on collection_type
            if self.collection_type == 'meeting':
                self.settings = resources.meeting_json
            elif self.collection_type == 'dataset':
                self.settings = resources.dataset_json
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ('approve_collection_items', 'Approve collection items'),
        )


class Item(models.Model):
    TYPES = (
        ('none', 'none'),
        ('project', 'project'),
        ('preprint', 'preprint'),
        ('registration', 'registration'),
        ('presentation', 'presentation'),
        ('website', 'website'),
        ('event', 'event'),
        ('meeting', 'meeting')
    )
    STATUS = (
        ('none', 'none'),
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('rejected', 'rejected')
    )
    CATEGORIES = (
        ('none', 'none'),
        ('talk', 'talk'),
        ('poster', 'poster')
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(choices=TYPES, max_length=200)
    status = models.CharField(choices=STATUS, null=True, max_length=200)
    source_id = models.CharField(null=True, blank=True, max_length=200)
    url = models.URLField(null=True, blank=True)
    collection = models.ForeignKey(to='Collection', related_name='items')
    created_by = models.ForeignKey(User)
    metadata = JSONField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateTimeField(null=True, blank=True, default=None)
    date_accepted = models.DateTimeField(null=True, blank=True, default=None)
    location = models.CharField(null=True, blank=True, default=None, max_length=200)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    category = models.CharField(choices=CATEGORIES, null=True, blank=True, max_length=200)
    file_link = models.CharField(null=True, blank=True, max_length=1000)
