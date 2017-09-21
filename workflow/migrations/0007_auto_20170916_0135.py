# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-16 01:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0006_auto_20170915_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterAlias',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('alias', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ParameterStub',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_stubs', to='workflow.Workflow')),
            ],
        ),
        migrations.RemoveField(
            model_name='widgetparametermapping',
            name='case',
        ),
        migrations.RemoveField(
            model_name='widgetparametermapping',
            name='parameter',
        ),
        migrations.RemoveField(
            model_name='widgetparametermapping',
            name='widget',
        ),
        migrations.RemoveField(
            model_name='widgetparametermapping',
            name='workflow',
        ),
        migrations.DeleteModel(
            name='WidgetParameterMapping',
        ),
        migrations.AddField(
            model_name='parameteralias',
            name='parameter_stub',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='workflow.ParameterStub'),
        ),
        migrations.AddField(
            model_name='parameteralias',
            name='widget',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_aliases', to='workflow.Widget'),
        ),
        migrations.AddField(
            model_name='parameteralias',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_aliases', to='workflow.Workflow'),
        ),
        migrations.AddField(
            model_name='parameter',
            name='stub',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='workflow.ParameterStub'),
        ),
        migrations.AlterUniqueTogether(
            name='parameterstub',
            unique_together=set([('workflow', 'name')]),
        ),
    ]