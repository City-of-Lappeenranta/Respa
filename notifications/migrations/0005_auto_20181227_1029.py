# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-12-27 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_auto_20181221_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='type',
            field=models.CharField(choices=[('reservation_requested', 'Reservation requested'), ('reservation_requested_official', 'Reservation requested official'), ('reservation_cancelled', 'Reservation cancelled'), ('reservation_confirmed', 'Reservation confirmed'), ('reservation_denied', 'Reservation denied'), ('reservation_created_with_access_code', 'Reservation created with access code'), ('catering_order_created', 'Catering order created'), ('catering_order_modified', 'Catering order modified'), ('catering_order_deleted', 'Catering order deleted'), ('reservation_comment_created', 'Reservation comment created'), ('catering_order_comment_created', 'Catering order comment created'), ('reservation_requested_payment', 'Reservation requested payment'), ('reservation_failed_payment', 'Reservation failed payment'), ('reservation_payment_successful', 'Reservation payment successful'), ('reservation_payment_successful_official', 'Reservation payment successful official')], db_index=True, max_length=100, unique=True, verbose_name='Type'),
        ),
    ]
