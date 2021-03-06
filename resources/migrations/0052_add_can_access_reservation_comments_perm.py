# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-09 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0051_add_can_view_reservation_extra_fields_perm'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unit',
            options={'ordering': ('name',), 'permissions': (('can_approve_reservation', 'Can approve reservation'), ('can_view_reservation_access_code', 'Can view reservation access code'), ('can_view_reservation_extra_fields', 'Can view reservation extra fields'), ('can_access_reservation_comments', 'Can access reservation comments')), 'verbose_name': 'unit', 'verbose_name_plural': 'units'},
        ),
    ]
