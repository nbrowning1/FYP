# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-10 14:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_general', models.CharField(max_length=1000)),
                ('feedback_positive', models.CharField(max_length=1000)),
                ('feedback_constructive', models.CharField(max_length=1000)),
                ('feedback_other', models.CharField(max_length=1000)),
                ('date', models.DateField()),
                ('anonymous', models.BooleanField()),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Module')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Student')),
            ],
        ),
    ]
