from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator
from django.conf import settings

from djmoney.models.fields import MoneyField

from basket.repository.business_logic.manager import OrderBusinessLogicLayer
from basket.repository.manager import OrderDataAccessLayerManager
from basket.helper.enums import OrderStatus
from painless.models import (
    TimeStampMixin,
    TruncateMixin
)


class Order(TimeStampMixin, TruncateMixin):
    """
    Order
    -----
    Order collects all the information needed for a purchase.
    for example : `receiver_name`, `postal_address`, etc.
    So when a customer wants to order a product, he/she
    must fill all the required fields in this table.

    PARAMS
    ------
    `packs` : A package is a group of items that are preselected for a
    fixed price. e,g, does the color affect the price?
    `status` : Determines what stage the user is in the order and
    it makes us reach a better category for orders.

    """
    DEFAULT_CURRENCY_SHOW_ON_SITE = settings.DEFAULT_CURRENCY_SHOW_ON_SITE

    footnote = models.TextField(
        _('footnote'),
        help_text=_('Additional user description for his/her order.')
    )
    # TODO: make it nullable if bank transaction doesn't work.
    transaction_number = models.CharField(
        _('transaction number'),
        max_length=255,
        unique=True,
        null=True,
        help_text=_("User's unique order number.")
    )
    logistic = models.ForeignKey(
        'logistic.Logistic',
        verbose_name=_('logistic'),
        related_name='orders',
        null=True,
        on_delete=models.PROTECT,
        help_text=_('Access to the related logistic of an order.')
    )
    vouchers = models.ManyToManyField(
        'voucher.Voucher',
        verbose_name=_('vouchers'),
        related_name='orders',
        blank=True,
        help_text=_('Access to the related voucher(s) of an order.')
    )
    packs = models.ManyToManyField(
        'warehouse.Pack',
        through='PackOrder',
        verbose_name=_('packs'),
        related_name='orders',
        help_text=_('Access to the related pack(s) of an order.')
    )

    dal = OrderDataAccessLayerManager()
    bll = OrderBusinessLogicLayer()
    objects = models.Manager()

    @property
    def status_list(self):
        status_list = [key.lower() for key in OrderStatus.__dict__.keys()
                       if not key.startswith('_')]
        status_list.remove('expiring')
        status_list.remove('cancelled')
        return status_list

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f'{self.id}'

    def __repr__(self):
        return f'{self.id}'
