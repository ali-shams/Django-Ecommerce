"""
Django Configurations that are related to security issues
"""
import os

from decouple import config

from .base import BASE_DIR

SECRET_KEY = config('SECRET_KEY')
PREPEND_WWW = config('PREPEND_WWW', cast=bool)

# ############################### #
#             EMAIL               #
# ############################### #
if config('EMAIL_DEBUG', cast=bool):
    EMAIL_BACKEND = 'django.core.mail.backend.console.EmailBackend'
else:
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    EMAIL_USER_TLS = config('EMAIL_USER_TLS', default=True, cast=bool)
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
    ADMINS = config('ADMINS', cast=lambda string: [s.strip() for s in string.split(',')])

# ############################### #
#            DATABASE             #
# ############################### #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'TEST': {
            'NAME': config('DB_TEST')
        }
    },
}

# ############################### #
#         UPLOAD SETTING          #
# ############################### #
if not os.path.exists(config('FILE_UPLOAD_TEMP_DIR')):
    os.makedirs(os.path.join(BASE_DIR, config('FILE_UPLOAD_TEMP_DIR')))
FILE_UPLOAD_TEMP_DIR = config('FILE_UPLOAD_TEMP_DIR')
FILE_UPLOAD_PERMISSIONS = 0o755
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', cast=int)
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', cast=int)

# ############################### #
#       SSL CONFIGURATION         #
# ############################### #
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER')
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF')
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS')
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', cast=bool)
USE_X_FORWARDED_HOST = True
SECURE_REDIRECT_EXEMPT = []
SECURE_REFERRER_POLICY = config('SECURE_REFERRER_POLICY')
SECURE_SSL_HOST = config('SECURE_SSL_HOST')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', cast=bool)
if config('SECURE_PROXY_SSL_HEADER', cast=bool):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ############################### #
#     CSRF SECURITY CONFIGS       #
# ############################### #
CSRF_COOKIE_AGE = config('CSRF_COOKIE_AGE', cast=int)
CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', cast=bool)
CSRF_COOKIE_NAME = config('CSRF_COOKIE_NAME')
CSRF_COOKIE_PATH = config('CSRF_COOKIE_PATH')
CSRF_COOKIE_SAMESITE = config('CSRF_COOKIE_SAMESITE').capitalize()
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', cast=bool)
CSRF_USE_SESSIONS = config('CSRF_USE_SESSIONS', cast=bool)
CSRF_HEADER_NAME = config('CSRF_HEADER_NAME')
