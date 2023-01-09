import logging

from django.db import transaction

from basket.models import (
    PackOrder,
    Order,
    Refund,
)
from warehouse.models import Expense

from basket.helper.exceptions import FailedRefund

logger = logging.getLogger(__name__)


class RefundServices:
    """
    Handles events that either require checks before happening or
    are transactions.
    """
    def refund_pack_order(self,
                          pack_order: PackOrder,
                          reason: str):
        with transaction.atomic():
            try:
                Refund.bll.add_to_refund(pack_order, reason)
                pack = pack_order.pack
                quantity = pack_order.quantity
                Expense.bll.update_count_stock(pack.sku, quantity, increase=True)
                Expense.bll.update_actual_count_stock(pack.sku, quantity, increase=True)

            except Exception as e:
                user = pack_order.order.user
                logger.warning(f'user: {user}, pack order {pack_order},action: '
                               f'`refund pack order`, error: `{e}`')
                raise FailedRefund(e)

    def refund_order(self,
                     order: Order,
                     reason: str):
        pack_orders = order.pack_orders.all()
        with transaction.atomic():
            try:
                for pack_order in pack_orders:
                    self.refund_pack_order(pack_order, reason)
            except Exception as e:
                user = pack_order.order.user
                logger.warning(f'user: {user}, order {order},action: '
                               f'`refund order`, error: `{e}`')
                raise FailedRefund(e)
