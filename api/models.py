from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from typedmodels.models import TypedModel


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    gravatar = models.URLField(blank=True)


class CollectionBase(TypedModel):
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User)
    created_by_org = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    settings = JSONField(default={})
    submission_settings = JSONField(default={})

    class Meta:
        permissions = (
            ('approve_items', 'Approve items'),
        )

    def __str__(self):
        return self.title


class Collection(CollectionBase):
    pass


class Meeting(CollectionBase):
    location = models.TextField(null=True, blank=True, default=None)
    start_date = models.DateTimeField(null=True, blank=True, default=None)
    end_date = models.DateTimeField(null=True, blank=True, default=None)


class Group(models.Model):
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    collection = models.ForeignKey(to='CollectionBase', related_name='groups')
    created_by = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class Item(models.Model):
    TYPES = (
        ('project', 'project'),
        ('preprint', 'preprint'),
        ('registration', 'registration'),
        ('presentation', 'presentation'),
        ('website', 'website'),
        ('event', 'event')
    )
    STATUS = (
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('rejected', 'rejected')
    )
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    type = models.TextField(choices=TYPES)
    status = models.TextField(choices=STATUS, null=True)
    source_id = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    collection = models.ForeignKey(to='CollectionBase', related_name='items')
    group = models.ForeignKey(to='Group', null=True, blank=True, default=None, related_name='items')
    created_by = models.ForeignKey(User)
    metadata = JSONField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateTimeField(null=True, blank=True, default=None)
    date_accepted = models.DateTimeField(null=True, blank=True, default=None)
    location = models.TextField(null=True, blank=True, default=None)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    category = models.TextField(null=True, blank=True, default=None)
