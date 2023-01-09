from rest_framework import serializers

from basket.models import Order
from warehouse.models import Pack


class OrderSerializer(serializers.ModelSerializer):


    quantity = serializers.IntegerField()
    class Meta:
        model = Order
        fields = (
            'footnote',
            'transaction_number',
            'status',
            'total_cost',
            'total_shipping_cost',
            'total_discount',
            'total_cost_without_discount',
            'total_cost_without_discount_and_shipping',
            # 'order_address',
            # 'logistic',
            # 'vouchers',
            'quantity',
            'packs',
        )
