from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    gravatar = models.URLField(blank=True)


class Collection(models.Model):
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User)
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


class Group(models.Model):
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    collection = models.ForeignKey(to='Collection', related_name='groups')
    created_by = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class Item(models.Model):
    TYPES = (
        ('project', 'project'),
        ('preprint', 'preprint'),
        ('registration', 'registration'),
        ('meeting', 'meeting'),
        ('website', 'website')
    )
    STATUS = (
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('rejected', 'rejected')
    )
    source_id = models.TextField()
    title = models.TextField()
    type = models.TextField(choices=TYPES)
    status = models.TextField(choices=STATUS)
    url = models.URLField()
    collection = models.ForeignKey(to='Collection', related_name='items')
    group = models.ForeignKey(to='Group', null=True, blank=True, default=None, related_name='items')
    created_by = models.ForeignKey(User)
    metadata = JSONField()
    date_added = models.DateTimeField(null=True, blank=True, default=None)
    date_submitted = models.DateTimeField(auto_now_add=True)
