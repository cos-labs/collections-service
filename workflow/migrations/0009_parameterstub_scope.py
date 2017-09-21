# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-16 19:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0008_auto_20170916_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterstub',
            name='scope',
            field=models.CharField(choices=[('CASE', 'Case'), ('WORKFLOW', 'Workflow'), ('GLOBAL', 'Global')], default='CASE', max_length=8),
        ),
    ]