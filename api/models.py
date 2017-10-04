from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    gravatar = models.URLField(blank=True)

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

class Collection(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User)
    created_by_org = models.CharField(null=True, blank=True, max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    settings = JSONField(default={}, blank=True)
    submission_settings = JSONField(default={}, blank=True)
    collection_type = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    workflow = models.ForeignKey(
        'workflow.Workflow',
        null=True,
        blank=True,
        related_name="collections",
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ('approve_collection_items', 'Approve collection items'),
        )


class Group(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    collection = models.ForeignKey(to='Collection', related_name='groups')
    created_by = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


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
    group = models.ForeignKey(to='Group', null=True, blank=True, default=None, related_name='items')
    created_by = models.ForeignKey(User)
    metadata = JSONField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateTimeField(null=True, blank=True, default=None)
    date_accepted = models.DateTimeField(null=True, blank=True, default=None)
    file_link = models.TextField(null=True, blank=True)
    location = models.CharField(null=True, blank=True, default=None, max_length=200)
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    category = models.CharField(choices=CATEGORIES, null=True, blank=True, max_length=200)
    file_link = models.CharField(null=True, blank=True, max_length=1000)
