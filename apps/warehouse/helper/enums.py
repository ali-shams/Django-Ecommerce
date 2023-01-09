from django.db import models
from django.utils.translation import gettext_lazy as _


class ImageStatus(models.TextChoices):
    First = ('first', _('First'))
    Second = ('second', _('Second'))
    Other = ('other', _('Other'))
