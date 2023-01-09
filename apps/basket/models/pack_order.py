from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from djmoney.models.fields import MoneyField

from basket.repository.business_logic.manager import PackOrderBusinessLogicLayer
from basket.repository.manager import PackOrderDataAccessLayerManager
from painless.models import (
    TimeStampMixin,
    TruncateMixin
)


class PackOrder(TimeStampMixin, TruncateMixin):
    """Pack order
    it serves like a virtual cart and hold information of one or more packs of an order# noqa
    until the purchase is completed. It organizes and distributes all order information# noqa
    including the order code, the package code(pack code),number of orders, available discount codes,# noqa
    The final price that the user pays, The final price that the user pays, The final price that the# noqa
    user pays and refund if there is any.

    PARAMS:
    ----
    `order`: access to the related order in the warehouse.
    `pack`: access to the related pack in the warehouse.
    `quantity`: quantity of the packs in each order.
    `vouchers`: the number of available vouchers for a pack or for an order.
    `cost`: total cost for the user pays.
    `buy_price`: total cast of each pack_order.
    `cost_without_discount`: he price of the pack or for an order without any discount.
    `refunded`: weather there is a refund or not.
    """
    DEFAULT_CURRENCY_SHOW_ON_SITE = settings.DEFAULT_CURRENCY_SHOW_ON_SITE

    quantity = models.PositiveIntegerField(
        _('quantity'),
        help_text=_('The number of packs in the order.')
    )
    cost = MoneyField(
        _('cost'),
        max_digits=14,
        decimal_places=2,
        default_currency=DEFAULT_CURRENCY_SHOW_ON_SITE,
        help_text=_('The final cost of the pack for the user to pay.')
    )
    cost_without_discount = MoneyField(
        _('cost without discount'),
        max_digits=14,
        decimal_places=2,
        default_currency=DEFAULT_CURRENCY_SHOW_ON_SITE,
        help_text=_('The final cost of the pack for the user to pay without any discount.')  # noqa
    )
    pack = models.ForeignKey(
        'warehouse.Pack',
        verbose_name=_('pack'),
        related_name='pack_orders',
        on_delete=models.PROTECT,
        help_text=_('Access to the related pack of a pack order.')
    )
    vouchers = models.ManyToManyField(
        'voucher.Voucher',
        verbose_name=_('vouchers'),
        related_name='pack_orders',
        blank=True,
        help_text=_('Access to the related voucher(s) of a pack order.')
    )

    dal = PackOrderDataAccessLayerManager()
    bll = PackOrderBusinessLogicLayer()
    objects = models.Manager()

    class Meta:
        verbose_name = _('Pack Order')
        verbose_name_plural = _('Pack Orders')

    def __str__(self):
        return f'{self.id}'

    def __repr__(self):
        return f'{self.id}'
