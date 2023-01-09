import os
import logging

from decouple import config
from sorl.thumbnail.log import ThumbnailLogHandler

BASE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), os.pardir)
)

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend'
]

ROOT_URLCONF = 'kernel.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, config('TEMPLATES_DIR'))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR, os.path.join(BASE_DIR, config('DIRS'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'string_if_invalid': 'ERROR: INVALID VARIABLE'
        },
    },
]

WSGI_APPLICATION = 'kernel.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ############################### #
#      INTERNATIONALIZATION       #
# ############################### #
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ############################### #
#             STATIC              #
# ############################### #
MEDIA_URL = config('MEDIA_URL')
MEDIA_ROOT = os.path.join(BASE_DIR, config('MEDIA_UPLOAD_DIR'))
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
FIXTURE_DIRS = tuple(config('FIXTURE_TEST_DIRS'))
STATIC_URL = config('STATIC_URL')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, config('STATIC_DIR')),
)
STATIC_ROOT = os.path.join(
    BASE_DIR, config('COLLECT_STATIC_DIR')
)

# ############################### #
#            LOGGING              #
# ############################### #
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)
