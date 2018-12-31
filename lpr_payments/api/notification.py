from hashlib import sha256
import logging
from lpr_payments.payments import CeeposException
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from lpr_purchase import settings
from lpr_purchase.models.purchase import Purchase


class PurchaseNotificationView(APIView):

    permission_classes = [permissions.AllowAny]
    parser_classes = (JSONParser, )
    qs = Purchase.objects.all()

    def post(self, request, format=None):

        req_obj = {
            'Id': request.data['Id'],
            'Status': request.data['Status'],
            'Reference': request.data['Reference'],
            'Hash': request.data['Hash'],
        }

        if not self._validate_notification(req_obj):
            raise CeeposException("Failed to validate notification hash", data=request.data)

        purchase = Purchase.objects.get(pk=req_obj['Id'], ceepos_reference=req_obj['Reference'])

        if purchase and req_obj['Status'] == 1:
            purchase.set_success()

        return Response(data={}, status=200)

    def _validate_notification(self, req_obj):
        str_to_check = '{Id}&{Status}&{Reference}'.format(**req_obj)
        str_to_check += '&' + settings.CPU_MERCHANT_SECRET

        return sha256(str_to_check.encode('utf-8')).hexdigest() == req_obj['Hash']
