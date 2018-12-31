# -*- coding: utf-8 -*-

from django.utils import timezone
from lpr_purchase import celery_app as app
from lpr_purchase.models.purchase import Purchase
from lpr_purchase.settings import PAYMENT_EXPIRATION_MINUTES, PAYMENT_LONG_EXPIRATION_MINUTES
from lpr_payments.payments import CeeposException
from resources.models.reservation import Reservation


@app.task
def remove_unpaid_reservations():

    purchases = Purchase.objects.filter(status=2)  # Query all "In progress" payments

    for p in purchases:
        try:
            reservation = p.reservation
        except Purchase.reservation.RelatedObjectDoesNotExist:
            continue

        expiration_seconds = PAYMENT_EXPIRATION_MINUTES * 60

        if reservation.resource.need_manual_confirmation:
            expiration_seconds = PAYMENT_LONG_EXPIRATION_MINUTES * 60

        if timezone.now().timestamp() - p.purchase_process_started.timestamp() > expiration_seconds:
            try:
                p.cancel_payment()
                p.set_failure()
                reservation = p.reservation
                reservation.delete()

            except CeeposException:
                # Couldn't cancel payment, maybe it was already paid?
                # Try again on next run of this task
                pass
