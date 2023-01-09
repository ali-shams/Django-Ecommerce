import os

import moneyed
from django.utils.translation import gettext_lazy as _
from django.contrib.messages import constants as messages
from decouple import config

from .base import (
    BASE_DIR,
    DEFAULT_APPS,
    MIDDLEWARE,
)

# ############################### #
#         CUSTOM PROJECT          #
# ############################### #
LOCAL_APPS = [
    'painless',
    'apps.account',
    'apps.feedback',
    'apps.warehouse',
]

THIRD_PARTY_PACKAGES = [
    # ############################### #
    #        DJANGO EXTENSIONS        #
    # ############################### #
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.postgres',

    # ############################### #
    #           EXTENSIONS            #
    # ############################### #
    # Model Packages
    'mptt',
    'django_countries',
    'djmoney',
    # Image Package
    'sorl.thumbnail',
    # Admin Packages
    'jalali_date',
    'colorfield',
    # Text Editor
    'ckeditor',
    'ckeditor_uploader',
    # Template Packages
    'django_better_admin_arrayfield',
]

INSTALLED_APPS = DEFAULT_APPS + LOCAL_APPS + THIRD_PARTY_PACKAGES

# ############################### #
#           MIDDLEWARE            #
# ############################### #
# To add documentation support in Django admin
MIDDLEWARE.append('django.contrib.admindocs.middleware.XViewMiddleware')

# ############################### #
#             MESSAGE             #
# ############################### #
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ############################### #
#             LOCALE              #
# ############################### #
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = (
    'en',
    'fa'
)
LANGUAGE_CODE = 'en'  # default language
LANGUAGES = (
    ('en', 'en-US'),
    ('fa', 'fa-IR'),
)

# ############################### #
#          MPTT PACKAGE           #
# ############################### #
MPTT_ADMIN_LEVEL_INDENT = 20
MPTT_ADMIN_LEVEL_INDENT = 20

# ############################### #
#           THUMBNAIL             #
# ############################### #
THUMBNAIL_KEY_PREFIX = config('THUMBNAIL_KEY_PREFIX')
THUMBNAIL_PREFIX = config('THUMBNAIL_PREFIX')
THUMBNAIL_FORMAT = config('THUMBNAIL_FORMAT')
THUMBNAIL_PRESERVE_FORMAT = config('THUMBNAIL_PRESERVE_FORMAT', cast=bool)
if config('DEBUG', default=False, cast=bool):
    THUMBNAIL_DEBUG = True
else:
    THUMBNAIL_DEBUG = False

# ############################### #
#         Django MONEY            #
# ############################### #
DEFAULT_CURRENCY_SHOW_ON_SITE = 'T'
USE_THOUSAND_SEPARATOR = True
RIAL = moneyed.add_currency(
    code='R',
    numeric='095',
    name=_('Iranian rial'),
    countries=('Iran',)
)
TOMAN = moneyed.add_currency(
    code='T',
    numeric='095',
    name=_('Iranian toman'),
    countries=('Iran',)
)
CURRENCIES = (
    'R',
    'T',
    'USD'
)
# ############################### #
#         AUTHENTICATION          #
# ############################### #
AUTH_USER_MODEL = 'account.User'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ############################### #
#            CK Editor            #
# ############################### #
CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                'Preview',
                'Maximize',

            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}

# ############################### #
#            SITE MAP             #
# ############################### #
SITE_ID = 1
