# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-11-15 10:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0066_support_for_django_2'),
    ]

    operations = [
       migrations.AddField(
            model_name='resource',
            name='owner_email',
            field=models.TextField(blank=True, null=True, verbose_name='Owner email'),
        )
    ]
