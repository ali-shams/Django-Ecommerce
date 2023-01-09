import logging

from django.db.models import Manager
from django.apps import apps
from django.db.models import F, Sum
from django.core.exceptions import ObjectDoesNotExist

from basket.helper.enums import OrderStatus
from basket.helper.exceptions import (PackNotInPackCart,
                                      DuplicatePackCartInCart,
                                      )
from basket.helper.enums import OrderStatus

from azbankgateways.models import Bank, PaymentStatus

logger = logging.getLogger(__name__)


class PackCartBusinessLogicLayer(Manager):
    """
    handles functions affecting PackCart model, such as adding or removing
    something to it or checking the state of it.
    """

    def get_total_price(
            self,
            pack_cart: 'PackCart'
    ):
        """
        calculates the total price of the pack.
        """
        price = self.filter(id=pack_cart.id) \
            .annotate(total_price=Sum('pack__expense__price')) \
            .first().total_price
        return price * pack_cart.quantity

    def get_total_buy_price(
            self,
            pack_cart: 'PackCart'
    ):
        """
        calculates the total `buy_price` of the pack.
        """
        buy_price = self.filter(id=pack_cart.id) \
            .annotate(total_buy_price=Sum('pack__expense__buy_price')) \
            .first().total_buy_price
        return buy_price * pack_cart.quantity


class CartBusinessLogicLayer(Manager):
    """
    handles functions affecting cart, such as adding or removing
    something to the cart or checking the state of it.
    """

    def is_pack_cart_in_cart(self,
                             cart: 'Cart',
                             pack_cart: 'PackCart') -> bool:
        """
        check whether given pack cart exists in cart.
        """
        return self.filter(slug=cart.slug, pack_carts=pack_cart).exists()

    def is_pack_in_the_cart(self, cart, pack):
        """
        to check whether the given pack is in the cart
        """
        return self.filter(id=cart.id, packs=pack).exists()

    def add_pack_to_cart(
            self,
            cart: 'Cart',
            given_pack: 'Pack',
            quantity: int):
        """
        Add the given `pack` to the given user's `cart` with given quantity.
        """
        if quantity < 1:
            raise ValueError('quantity should be greater than or equal 1 however'
                             f' {quantity} was given')
        PackCart = apps.get_model('basket', 'PackCart')
        if self.is_pack_in_the_cart(cart, given_pack):
            PackCart.bll.filter(cart=cart, pack=given_pack) \
                .update(quantity=F('quantity') + quantity)
            if PackCart.bll.filter(cart=cart, pack=given_pack).count() == 1:
                pack_cart = PackCart.bll.get(cart=cart, pack=given_pack)
            else:
                raise DuplicatePackCartInCart('there\'s more than one pack_cart'
                                              'with with pack in this cart')
        else:
            pack_cart = PackCart.bll.create(
                quantity=quantity,
                cart=cart,
                pack=given_pack,
            )
        return pack_cart

    def del_pack_cart_from_cart(self,
                                cart: 'Cart',
                                pack_sku: str):
        """
        Delete the given pack_sku from the given `cart`.
        DESC
        _____
        Every time the user deletes a `pack_cart` from his/her `cart`,
        we do as follows in the `pack_cart` table:
            1. check if the `pack_cart` is actually in the `cart`.
            2. delete the `pack_cart` from the `cart`.
        """
        PackCart = apps.get_model('basket', 'PackCart')

        try:
            pack_cart = PackCart.dal.get(cart=cart, pack__sku=pack_sku)
        except ObjectDoesNotExist as e:
            logger.error(f'pack cart objects with cart:{cart} and pack sku of\
                :{pack_sku} does not exists with trace: {str(e)}', exc_info=True)
            raise ObjectDoesNotExist()

        if self.is_pack_cart_in_cart(cart, pack_cart):
            PackCart.bll.filter(id=pack_cart.id).delete()
        else:
            raise PackNotInPackCart(f'PackCart {pack_cart.slug}'
                                    f' does not exist in cart {cart.slug}')

    def update_pack_cart_quantity(
            self,
            cart: 'Cart',
            pack_cart: 'PackCart',
            increment: bool
    ):
        """
        adds or subtracts 1 from given `pack_cart`'s quantity.
        raises ValueError if given increment isn't in list if accepted increments.
        calling '-' on a `PackCart` with quantity 1 will remove it.
        """
        # todo change name of this function to increment...
        PackCart = apps.get_model('basket', 'PackCart')
        if self.is_pack_cart_in_cart(cart, pack_cart):
            if increment:
                PackCart.bll.filter(id=pack_cart.id) \
                    .update(quantity=(pack_cart.quantity + 1))
            else:
                if pack_cart.quantity > 1:
                    PackCart.bll.filter(id=pack_cart.id) \
                        .update(quantity=(pack_cart.quantity - 1))
                else:
                    self.del_pack_cart_from_cart(cart, pack_cart.pack.sku)
        else:
            raise PackNotInPackCart(f"Given pack with sku: {pack_cart.slug}"
                                    f"doesn't exist in pack cart.")
