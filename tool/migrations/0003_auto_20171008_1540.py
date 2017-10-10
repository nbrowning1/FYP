# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-08 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0002_auto_20171007_2242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lecture',
            name='date',
        ),
        migrations.AddField(
            model_name='lecture',
            name='semester',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lecture',
            name='week',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]