from enum import Enum


class ImageExtensionEnum(Enum):
    JPG = ['JPG', 'JPEG', 'jpg', 'jpeg']
    PNG = ['PNG', 'png']


class RegexPatternEnum(Enum):
    Iran_phone_number = r'^(\+98|0)?9\d{9}$'
    International_phone_number = r'^(\(?\+?[0-9]*\)?)?[0-9_\- \(\)]*$'


class URLRegexPatternEnum(Enum):
    Url_slug_finder = r'(?P<slug>[-\w]+)'
    Url_pk_finder = r'(?P<pk>\d+)'
    Url_username_finder = r'(?P<username>[\w.@+-]+)'
    Url_year_finder = r'(?P<year>[0-9]{4})'
    Url_month_finder = r'(?P<month>[0-9]{2})'
    Url_day_finder = r'(?P<day>[0-9]{2})'


class VisualStudioCodeEnum(Enum):
    Image_source = r'src="([A-Za-z0-9/-]+\.[a-z]+)"'
    Replace_django_static = r'src="{% static \'$1\' %}"'
