# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-28 12:33
from __future__ import unicode_literals

from django.db import migrations


def migrate_business_id(apps, schema_editor):
    Reservation = apps.get_model("resources", "Reservation")
    for res in Reservation.objects.exclude(business_id=''):
        res.reserver_id = res.business_id
        res.save(update_fields=['reserver_id'])

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0035_add_reserver_id'),
    ]

    operations = [
        migrations.RunPython(migrate_business_id)
    ]
