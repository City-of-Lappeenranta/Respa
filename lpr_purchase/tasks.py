# -*- coding: utf-8 -*-

import csv
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


# This task should probably be moved to a different file in the future
@app.task
def generate_reservation_report():
    DATETIME_FORMAT = "%Y.%m.%d %H:%M"
    reservations = Reservation.objects.all()

    fields = ["resource_name", "unit_name", "reservation_start",
              "reservation_end", "paid_amount", "purchase_id",
              "client_email", "created_at", "verbose_status"]

    with open("/tmp/export.csv", "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write csv header
        writer.writerow(fields)

        for r in reservations:
            row = []
            row.append(r.resource.name)
            row.append(r.resource.unit.name)
            row.append(r.begin.strftime(DATETIME_FORMAT))
            row.append(r.end.strftime(DATETIME_FORMAT))
            if r.purchase:
                row.append(r.purchase.price_vat)
                row.append(r.purchase.id)
            else:
                row.append("")
                row.append("")
            row.append(r.reserver_email_address)
            row.append(r.created_at.strftime(DATETIME_FORMAT))
            row.append(r.state)

            writer.writerow(row)

        csvfile.close()
