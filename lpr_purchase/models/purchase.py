import json
from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from resources.models.base import AutoIdentifiedModel, ModifiableModel
from resources.models.resource import Resource, ResourceGroup
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.models import AnonymousUser
from lpr_purchase.settings import CPU_MERCHANT_ID, CPU_MERCHANT_SECRET, CPU_PAYMENT_NOTIFICATION_ADDRESS
from lpr_payments.payments import CeeposPaymentRequestAPIClient, CeeposProduct, CeeposPaymentRequest, \
    CeeposPaymentCancellationAPIClient, CeeposPaymentCancellation


class Purchase(ModifiableModel):
    purchase_code = models.CharField(verbose_name=_('Purchase code'), max_length=40)
    vat_percent = models.IntegerField(choices=[(0, '0'), (10, '10'), (14, '24'), (24, '24')], default=24)
    price_vat = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    product_name = models.CharField(verbose_name=_('Product name'), max_length=100, blank=True)

    purchase_process_started = models.DateTimeField(verbose_name=_('Purchase process started'), default=timezone.now)
    purchase_process_success = models.DateTimeField(verbose_name=_('Purchase process success'), blank=True, null=True)
    purchase_process_failure = models.DateTimeField(verbose_name=_('Purchase process failure'), blank=True, null=True)

    status = models.IntegerField(blank=True, null=True)
    ceepos_reference = models.IntegerField(blank=True, null=True)
    payment_address = models.CharField(verbose_name=_('Payment link'), max_length=200, blank=True, null=True)

    def request_payment(self):
        client = CeeposPaymentRequestAPIClient(CPU_MERCHANT_ID, CPU_MERCHANT_SECRET)
        req = CeeposPaymentRequest(order_id=self.pk, notification_address=CPU_PAYMENT_NOTIFICATION_ADDRESS)
        req.add_product(CeeposProduct(product_id=self.purchase_code, price=int(self.price_vat * 100)))

        res = client.initialize_payment(req)
        self.payment_address = res.payment_address
        self.status = res.status
        self.ceepos_reference = res.reference
        self.save()
        return self.payment_address

    def cancel_payment(self):
        client = CeeposPaymentCancellationAPIClient(CPU_MERCHANT_ID, CPU_MERCHANT_SECRET)
        req = CeeposPaymentCancellation(order_id=self.pk)

        res = client.cancel_payment(req)

        self.ceepos_reference = res.reference
        self.status = res.status
        self.save()

    def set_success(self):
        if self.purchase_process_failure or self.purchase_process_success:
            raise SuspiciousOperation(_('Purchase callback has already returned'))

        self.purchase_process_success = timezone.now()
        self.status = 1
        self.finished = timezone.now()
        self.save()
        self.reservation.send_payment_success_mail()

    def set_failure(self, user=AnonymousUser()):
        if self.purchase_process_failure or self.purchase_process_success:
            raise SuspiciousOperation(_('Purchase callback has already returned'))

        self.purchase_process_failure = timezone.now()
        self.save()
        self.reservation.send_payment_failed_mail()

    def set_finished(self):
        if self.finished:
            raise SuspiciousOperation(_('Purchase is already finished'))
        self.finished = timezone.now()
        self.save()

    def is_success(self):
        return bool(self.purchase_process_success)

    def is_finished(self):
        return bool(self.finished)

    def __str__(self):
        return "%s" % (self.pk)
