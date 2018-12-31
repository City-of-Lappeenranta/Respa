import json
import logging
import requests
from hashlib import sha256
from lpr_purchase.settings import *

class CeeposException(Exception):
    def __init__(self, message=None, code=None, data=None):
        self.code = code
        self.message = message
        self.data = data

    def __str__(self):
        return " %s caused by request data %s." % (self.message, self.data)

# Maksu maksettu -vahvistus sekä ohjelmallinen maksukuittaus
class CeeposPaymentPaidAck(object):
    def __init__(self, order_id, status, reference):
        self.order_id = order_id
        self.status = status
        self.reference = reference

    def calculate_checksum(self):
        str_to_check = self.order_id+'&'+self.status+'&'+self.reference+'&'+CPU_MERCHANT_SECRET
        checksum = sha256(str_to_check)
        return checksum

# Maksulähetyksen vastaus
class CeeposPaymentRequestAck(object):
    def __init__(self, purchase_id, status_code, reference, action, payment_address):
        self.purchase_id = purchase_id
        self.status = status_code
        self.reference = reference
        self.action = action
        self.payment_address = payment_address


# Maksun perumisen vastaus
class CeeposPaymentCancellationAck(object):
    def __init__(self, order_id, status, reference, action):
        self.order_id = order_id
        self.status = status
        self.reference = reference
        self.action = action

    def calculate_checksum(self):
        str_to_check = self.order_id+'&'+self.status+'&'+self.reference+'&'+self.action+'&'+CPU_MERCHANT_SECRET
        checksum = sha256(str_to_check)
        return checksum


class CeeposPaymentRequest(object):
    _products = []

    def __init__(self, order_id, description="", email="", first_name="", last_name="", language="fi", return_address="", notification_address="",
                 action='new payment'):
        self.order_id = order_id
        self.action = action
        self.description = description
        self._products = []
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.language = language

        if not return_address:
            self.return_address = VARAAMO_RETURN_URL
        else:
            self.return_address = return_address

        self.notification_address = notification_address

    def add_product(self, product):
        self._products.append(product)

    def get_hashable_products_string(self):
        # In our case we only have 1 product, with parameters Code and Price

        hashable_string = ""
        for product in self._products:
            hashable_string += '&' + product.product_id
            hashable_string += '&' + str(product.price)

        return hashable_string


    def calculate_checksum(self):
        str_to_check = CPU_API_VERSION+'&'+CPU_MERCHANT_ID+'&'+str(self.order_id)+'&'+str(CPU_ACCESS_MODE)+'&'+self.action
        if self.description:
            str_to_check += '&' + self.description

        str_to_check += self.get_hashable_products_string()

        if self.email:
            str_to_check += '&' + self.email
        if self.first_name:
            str_to_check += '&' + self.first_name
        if self.last_name:
            str_to_check += '&' + self.last_name
        if self.language:
            str_to_check += '&' + self.language

        str_to_check += '&'+self.return_address+'&'+self.notification_address+'&'+CPU_MERCHANT_SECRET
        checksum = sha256(str_to_check.encode('utf-8'))
        return checksum

    def get_data(self):
        data = {
            'ApiVersion': CPU_API_VERSION,
            'Source': CPU_MERCHANT_ID,
            'Id': str(self.order_id),
            'Mode': CPU_ACCESS_MODE,
            'Action': self.action,
            'Products': [p.get_data() for p in self._products],
            'ReturnAddress': self.return_address,
            'NotificationAddress': self.notification_address,
        }

        if (self.description): data['Description'] = self.description
        if (self.email): data['Email'] = self.email
        if (self.first_name): data['FirstName'] = self.first_name
        if (self.last_name): data['LastName'] = self.last_name
        if (self.language): data['Language'] = self.language

        data['Hash'] = self.calculate_checksum().hexdigest()
        return data


class CeeposPaymentCancellation(object):
    def __init__(self, order_id, action='delete payment'):
        self.order_id = order_id
        self.action = action

    def calculate_checksum(self):
        str_to_check = CPU_API_VERSION+'&'+CPU_MERCHANT_ID+'&'+str(self.order_id)+'&'+str(CPU_ACCESS_MODE)+'&'+self.action+'&'+CPU_MERCHANT_SECRET
        checksum = sha256(str_to_check.encode('utf-8')).hexdigest()
        return checksum

    def get_data(self):
        return {
            'ApiVersion': CPU_API_VERSION,
            'Source': CPU_MERCHANT_ID,
            'Id': str(self.order_id),
            'Mode': CPU_ACCESS_MODE,
            'Action': self.action,
            'Hash': self.calculate_checksum()
        }


class CeeposProduct(object):
    def __init__(self, product_id, price, description="", taxcode="", amount=1):
        self.product_id = product_id
        self.amount = amount
        self.price = price
        self.description = description
        self.taxcode = taxcode

    def get_data(self):
        return {
            'Code': self.product_id,
            'Price': self.price
        }


class CeeposPaymentRequestAPIClient(object):
    def __init__(self, merchant_id, merchant_secret):
        self.merchant_id = merchant_id
        self.merchant_secret = merchant_secret

    def initialize_payment(self, payment):
        url = CPU_SERVICE_URL
        payment_data = payment.get_data()
        r = self.request(url, payment_data)

        j = r.json()
        if j['Status'] not in [0, 1, 2]:
            # If creation was other than a success, throw exception
            # Later we probably want to have proper handling for this
            # TODO: Implement proper error case handling
            raise CeeposException(r.text, data=payment_data)

        if not self.validate_callback_data(j):
            raise CeeposException("Failed to validate response", data=j)

        return CeeposPaymentRequestAck(j['Id'], j['Status'], j['Reference'], j['Action'], j['PaymentAddress'])

    def request(self, url, data):
        headers = {'Content-Type': 'application/json'}
        return requests.post(url, headers=headers, json=data)

    def validate_callback_data(self, data):
        try:
            # Validate success callback
            str_to_check = '{Id}&{Status}&{Reference}&{Action}&{PaymentAddress}'.format(**data)
            str_to_check += '&' + CPU_MERCHANT_SECRET
            checksum = sha256(str_to_check.encode('utf-8'))
            return checksum.hexdigest() == data['Hash']
        except KeyError:
            return False


class CeeposPaymentCancellationAPIClient(object):
    def __init__(self, merchant_id, merchant_secret):
        self.merchant_id = merchant_id
        self.merchant_secret = merchant_secret

    def cancel_payment(self, cancellation):
        url = CPU_SERVICE_URL
        cancellation_data = cancellation.get_data()
        r = self.request(url, cancellation_data)

        j = r.json()
        if j['Status'] != 1:
            # If cancellation did not succeed, raise CeeposException
            raise CeeposException(r.text, data=cancellation_data)

        if not self.validate_callback_data(j):
            raise CeeposException("Failed to validate cancellation response", data=j)

        return CeeposPaymentCancellationAck(j['Id'], j['Status'], j['Reference'], j['Action'])

    def request(self, url, data):
        headers = {'Content-Type': 'application/json'}
        return requests.post(url, headers=headers, json=data)

    def validate_callback_data(self, data):
        try:
            # Validate success callback
            str_to_check = '{Id}&{Status}&{Reference}&{Action}'.format(**data)
            str_to_check += '&' + CPU_MERCHANT_SECRET
            checksum = sha256(str_to_check.encode('utf-8'))
            return checksum.hexdigest() == data['Hash']
        except KeyError:
            return False
