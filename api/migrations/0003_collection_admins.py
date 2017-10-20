# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-19 11:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('api', '0002_auto_20171016_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='admins',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='collection', to='auth.Group'),
        ),
    ]