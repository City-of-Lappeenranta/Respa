# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-11-15 14:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0070_auto_20181115_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='purchase',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lpr_purchase.Purchase', verbose_name='Purchase'),
        ),
    ]
