import logging
from typing import Any, Dict

from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from azbankgateways.models import Bank, PaymentStatus
from azbankgateways import default_settings as bank_settings

from basket.helper.enums import OrderStatus
from basket.models import Order


logger = logging.getLogger(__name__)


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/basket/checkout-success.html'
    page_title = _('Checkout')

    def render_to_response(self, context: Dict[str, Any], **response_kwargs: Any):
        context['error'] = False
        tracking_code = self.request.GET.get(bank_settings.TRACKING_CODE_QUERY_PARAM, None)

        if not tracking_code:
            return redirect(reverse('pages:home'))

        try:
            order, bank_record = Order.dal.get_order_with_bank_record(transaction_number=tracking_code)

        except ObjectDoesNotExist as e:
            logger.error(f"There is no tracking code as: {tracking_code} for user: {self.request.user} error: {str(e)}", exc_info=True)
            return redirect(reverse('pages:home'))

        except Exception as e:
            logger.error(
                f"There was a problem with checkout-success with tracking code\
                    : {tracking_code} for user: {self.request.user} error: {str(e)}", exc_info=True)
            context['error'] = True
            context['tracking_code'] = tracking_code
            return super().render_to_response(context, **response_kwargs)

        if not Order.bll.verify_transaction_and_user(
            order=order,
            request_user=self.request.user,
        ):
            return redirect(reverse('pages:home'))

        # # todo uncomment this below line
        # # CartWithModel(request).flush()

        order = Order.bll.update_order_with_bank_record_and_warehouse_data(
            order=order,
            bank_record=bank_record
        ) # this is where the order status and warehouse data updates

        if bank_record.status == PaymentStatus.COMPLETE:
            context['success'] = True
            context['postal_address'] = order.order_address.postal_address
            context['province'] = order.order_address.province
            context['city'] = order.order_address.city
            context['postal_code'] = order.order_address.postal_code
            context['order_packs'], context['total_cost'] = \
                Order.dal.get_all_pack_orders_with_total_order_cost(order=order)

        else:
            context['success'] = False

        context['tracking_code'] = tracking_code
        context['order_submit_date'] = order.created

        return super().render_to_response(context, **response_kwargs)