import logging

from django.db import transaction

from basket.models import Order
from warehouse.models import Expense

from basket.helper.exceptions import OrderFailedToFinalize

logger = logging.getLogger(__name__)


class PostPaymentServices:
    """
    Handles events after a successful payment that either require checks before
    happening or are transactions.
    """
    def after_successful_payment(self,
                                 order: Order,
                                 ):
        """
        After receiving a success payment from bank the following should happen:
            1- change order status to `processing`
            2- update count stock and actual count stock
        """
        user = order.user
        transaction_number = order.transaction_number
        with transaction.atomic():
            try:
                Order.bll.update_order_status(order, 'processing')
                pack_orders = order.pack_orders.select_related('pack').all()
                for pack_order in pack_orders:
                    pack = pack_order.pack
                    quantity = pack_order.quantity
                    Expense.bll.update_count_stock(pack.sku, quantity, increase=False)
                    Expense.bll.update_actual_count_stock(pack.sku, quantity, increase=False)
            except Exception as e:
                logger.critical(f'user: `{user}`, transaction number: '
                                f'`{transaction_number}`, action: `finalize '
                                f'payment`, error: `{e}`', exc_info=True)
                raise OrderFailedToFinalize(e)
