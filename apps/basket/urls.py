from django.urls import re_path
from basket.views import (
    CartView,
    remove_pack_from_cart,
    add_pack_to_cart,
    CheckoutView,
    CheckoutSuccessView,
)
app_name = 'basket'

urlpatterns = [
    re_path(r'^basket/cart/$', CartView.as_view(), name='cart'),
    # re_path(r'^basket/cart/(?P<remove_pack>[\w\-]+)$', CartView.as_view(), name='cart-remove'),
    re_path(r'^basket/cart-remove/(?P<pack_sku>[\w\-]+)$', remove_pack_from_cart, name='cart-remove'),
    re_path(r'^basket/cart-add/(?P<pack_sku>[\w\-]+)$', add_pack_to_cart, name='cart-add'),
    re_path(r'^basket/checkout/$', CheckoutView.as_view(), name='checkout'),
    re_path(r'^basket/checkout/success/$', CheckoutSuccessView.as_view(), name='checkout-success'),

]