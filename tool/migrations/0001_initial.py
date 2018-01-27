# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-27 14:24
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=250)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_code', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='Must be a valid module code e.g. COM101', regex='^[A-Z]{3,4}[0-9]{3}$')])),
                ('module_crn', models.CharField(max_length=50)),
                ('courses', models.ManyToManyField(to='tool.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses', models.ManyToManyField(to='tool.Course')),
                ('modules', models.ManyToManyField(to='tool.Module')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=6, validators=[django.core.validators.RegexValidator(message='Must be a valid device ID e.g. 10101C', regex='^[A-Za-z0-9]{6}$')])),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Course')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attended', models.BooleanField()),
                ('lecture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Lecture')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Student')),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='students',
            field=models.ManyToManyField(to='tool.Student'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Module'),
        ),
    ]
