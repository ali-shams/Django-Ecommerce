from import_export import resources
from basket.models import Order


class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = (
            "footnote",
            "transaction_number",
            "status",
            "total_cost",
            "total_shipping_cost",
            "total_discount",
            "total_cost_without_discount",
            "total_cost_without_discount_and_shipping",
            "user__phone_number",
            "logistic__title",
            "vouchers__title",
            "packs",
            'created',
        )
