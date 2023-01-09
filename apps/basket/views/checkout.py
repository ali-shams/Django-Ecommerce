import logging
from typing import Callable, Any, Dict

from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect

from painless.utils.iranian_bank_gateway import IranianBankGateway
from logistic.forms import AddressForm
from logistic.models import Address
from basket.forms import OrderAddressForm
from basket.models import Cart, Order


logger = logging.getLogger(__name__)


class CheckoutView(LoginRequiredMixin, TemplateView):
    # todo login URL if not logged in
    template_name = 'pages/basket/checkout.html'
    page_title = _('Checkout')
    page_path = ('home', 'checkout')

    def check_if_cart_is_empty(self, context):
        if not context['cart_packs']: 
            return True
        return False

    def create_or_get_address(self, order_form):
        filters = {
            "country": order_form.data.get('country'),
            "province": order_form.data.get('province'),
            "city": order_form.data.get('city'),
            "postal_address": order_form.data.get('postal_address'),
            "postal_code": order_form.data.get('postal_code'),
            "house_number": order_form.data.get('house_number'),
            "building_unit": order_form.data.get('building_unit'),
            "receiver_first_name": order_form.data.get('receiver_first_name'),
            "receiver_last_name": order_form.data.get('receiver_last_name'),
            "receiver_phone_number": order_form.data.get('receiver_phone_number'),
        }

        return Address.bll.create_or_get_address(user=self.request.user, filters=filters)

    def post(self, request, *args, **kwargs):
        order_address_form = OrderAddressForm(request.POST)

        context = dict()
        context['cart_packs'], context['total_cost'] = \
            Cart.dal.get_all_pack_carts_with_total_cart_cost(cart=self.request.user.cart)

        if self.check_if_cart_is_empty(context):
            return redirect(reverse('basket:cart'))

        if order_address_form.is_valid():
            try:
                address = self.create_or_get_address(order_address_form)
            except Exception as e:
                logger.error(f'failed to get or create user address for checkout: {str(e)}', exc_info=True)
                messages.error(self.request, _("There was something wrong with your addresses"))
                return redirect(reverse('basket:checkout'))

            order_address = order_address_form.save()

            # todo use transform_cart_to_order from PrePaymentService
            order = Order.bll.add_to_order(
                user=request.user,
                order_address=order_address,
                footnote=request.POST.get('footnote')
            )

            bank = IranianBankGateway(
                amount=order.total_cost.amount,
                order=order
            )

            return bank.go_to_gateway(self.request)

        else:
            messages.error(self.request, _("There was something wrong with your addresses"))
            return redirect(reverse('basket:checkout'))

    def render_to_response(self, context: Dict[str, Any], **response_kwargs: Any) -> Callable:
        # todo: check if each pack cart is available each time that cart is 
        # being loaded.

        context['cart_packs'], context['total_cost'] = \
            Cart.dal.get_all_pack_carts_with_total_cart_cost(cart=self.request.user.cart)

        if self.check_if_cart_is_empty(context):
            return redirect(reverse('basket:cart'))

        address = Address.bll.get_and_update_user_default_address(user=self.request.user)

        if address:
            form = AddressForm(instance=address)
        else:
            form = AddressForm()

        context['form'] = form

        return super().render_to_response(context, **response_kwargs)
