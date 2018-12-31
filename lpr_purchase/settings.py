from respa.settings import INSTALLED_APPS
import environ

INSTALLED_APPS += [
    'lpr_payments'
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_FROM = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True

env = environ.Env(
    CPU_SERVICE_URL=(str, ''),
    CPU_API_VERSION=(str, '2.1.2'),
    CPU_ACCESS_MODE=(int, 3),  # Should always be 3 but we reserve the possibility to overwrite it from .env
    CPU_MERCHANT_ID=(str, ''),
    CPU_MERCHANT_SECRET=(str, ''),
    VARAAMO_RETURN_URL=(str, '')
)

environ.Env.read_env()

CPU_SERVICE_URL = env('CPU_SERVICE_URL')
CPU_API_VERSION = env('CPU_API_VERSION')
CPU_ACCESS_MODE = env('CPU_ACCESS_MODE')
CPU_MERCHANT_ID = env('CPU_MERCHANT_ID')
CPU_MERCHANT_SECRET = env('CPU_MERCHANT_SECRET')
CPU_PAYMENT_NOTIFICATION_ADDRESS = env('CPU_PAYMENT_NOTIFICATION_ADDRESS')
VARAAMO_RETURN_URL = env('VARAAMO_RETURN_URL')

PAYMENT_EXPIRATION_MINUTES = 15
PAYMENT_LONG_EXPIRATION_MINUTES = 60 * 24
