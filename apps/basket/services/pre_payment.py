import logging
from typing import Dict

from django.db import transaction

from basket.models import (
    Cart,
    PackOrder,
    Order,
    OrderAddress
)
from warehouse.models import Pack
from logistic.models import Logistic
from voucher.models import Voucher
from account.models import User
from basket.helper.exceptions import (FailedAddToCart,
                                      OrderFailedToCreate,
                                      )

logger = logging.getLogger(__name__)


class PrePaymentServices:
    """
    Handles events before a successful payment that either require checks before
    happening or are transactions.
    """

    def check_conditions(self,
            cart: Cart,
            pack: Pack,
            quantity: int) -> bool:
        if Pack.bll.is_available(pack.sku) \
                            and Pack.bll.is_pack_in_stock(pack.sku, quantity) \
                            and User.bll.is_active(cart.user):
            return True
        else:
            return False

    def update_cart(self, cart: Cart, packs_with_quantity: Dict[str, int]) -> bool:
        pack_carts = list()
        for pack, quantity in packs_with_quantity.items():
            if self.check_conditions(
                cart=cart,
                pack=pack,
                quantity=quantity):

                obj = cart.pack_carts.get(pack=pack)
                obj.quantity = quantity
                pack_carts.append(obj)

            else:
                return False
        Cart.bll.bulk_update_pack_carts_quantity(pack_carts)
        return True

    def add_pack_to_cart(
            self,
            cart: Cart,
            pack: Pack,
            quantity: int):
        user = cart.user
        try:
            if self.check_conditions(
                cart=cart,
                pack=pack,
                quantity=quantity
            ):
                Cart.bll.add_pack_to_cart(cart, pack, quantity)
        except Exception as e:
            logger.warning(f'user: `{user}`, pack: `{pack}`, '
                           f'action: `add pack to cart` error: `{e}`', exc_info=True)
            raise FailedAddToCart(e)

    def transform_cart_to_order(
            self,
            footnote: str,
            transaction_number: int,
            user: User,
            logistic: Logistic,
            voucher: Voucher,
            order_address: OrderAddress,
    ):
        """
        After user tries to pay for the cart, the following should happen:
            1- create an order
            2- transform each pack_cart to pack_order
            3- empty the cart by deleting all pack_carts
        """
        cart = user.cart
        with transaction.atomic():
            try:
                # TODO: add voucher checks, and maybe pack too.
                order = Order.bll.add_to_order(
                    footnote=footnote,
                    transaction_number=transaction_number,
                    user=user,
                    logistic=logistic,
                    voucher=voucher,
                    order_address=order_address,
                )
                # Order.bll.add_order_many_to_many_rels(order)
                pack_carts = cart.pack_carts.all()
                for pack_cart in pack_carts:
                    PackOrder.bll.add_to_pack_order(pack_cart, order, voucher)
                Cart.bll.del_all_pack_carts(cart)
            except Exception as e:
                logger.warning(f'transaction number: `{transaction_number}` '
                               f'action: `transform cart to order`, error: `{e}`', exc_info=True)
                raise OrderFailedToCreate(e)
