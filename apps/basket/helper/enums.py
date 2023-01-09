from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.TextChoices):
    Waiting = ('waiting', _('waiting'))
    Processing = ('processing', _('Processing'))
    Shipped = ('shipped', _('Shipped'))
    Delivered = ('delivered', _('Delivered'))
    Completed = ('completed', _('Completed'))
    Expiring = ('expiring', _('Expiring'))
    Cancelled = ('cancelled', _('Cancelled'))