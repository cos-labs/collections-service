# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-04 17:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20171130_1938'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collection',
            options={'permissions': (('moderate_collection', 'Moderate collection'),)},
        ),
    ]