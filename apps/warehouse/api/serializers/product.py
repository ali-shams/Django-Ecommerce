from rest_framework import serializers

from apps.warehouse.models import Product


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    def get_queryset(self):
        return Product.dal.get_available_items()

    class Meta:
        model = Product
        fields = [
            'url',
            'title',
            'description',
            'subtitle',
            'brand',
            'category',
            'is_active',
            'is_voucher_active',
            'created'
        ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
            'category': {'lookup_field': 'slug'},
            'brand': {'lookup_field': 'slug'},
        }
