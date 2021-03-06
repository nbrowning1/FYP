# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-25 21:02
from __future__ import unicode_literals

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import encrypted_model_fields.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='EncryptedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', encrypted_model_fields.fields.EncryptedCharField(blank=True, verbose_name='first name')),
                ('last_name', encrypted_model_fields.fields.EncryptedCharField(blank=True, verbose_name='last name')),
                ('email', encrypted_model_fields.fields.EncryptedEmailField(blank=True, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
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
            ],
        ),
        migrations.CreateModel(
            name='ModuleFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_general', models.CharField(max_length=1000)),
                ('feedback_positive', models.CharField(max_length=1000)),
                ('feedback_constructive', models.CharField(max_length=1000)),
                ('feedback_other', models.CharField(blank=True, max_length=1000)),
                ('date', models.DateField()),
                ('anonymous', models.BooleanField()),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Module')),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('colourblind_opts_on', models.BooleanField(default=False)),
                ('attendance_range_1_cap', models.IntegerField(default=25)),
                ('attendance_range_2_cap', models.IntegerField(default=50)),
                ('attendance_range_3_cap', models.IntegerField(default=75)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
            model_name='modulefeedback',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tool.Student'),
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
        migrations.AddField(
            model_name='course',
            name='modules',
            field=models.ManyToManyField(to='tool.Module'),
        ),
        migrations.AlterUniqueTogether(
            name='module',
            unique_together=set([('module_code', 'module_crn')]),
        ),
    ]
