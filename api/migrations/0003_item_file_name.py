# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-24 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20171020_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='file_name',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
