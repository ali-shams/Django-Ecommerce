from django.db import models
from django_filters import (
    FilterSet,
    CharFilter,
    Filter
)

from django_filters.widgets import (
    LinkWidget
)

from warehouse.models import Product
from warehouse.models import Category

class ProductFilter(FilterSet):
    cat = CharFilter(
        method='filter_category_title'
    )
    color = CharFilter(
        method='filter_color_title'
    )
    brand = CharFilter(
        method='filter_brand_title'
    )
    tag = CharFilter(
        method='filter_tag_title'
    )
    is_available = CharFilter(
        method='filter_in_stock_availability'
    )

    class Meta:
        model = Product
        fields = [
            'cat',
            'color',
            'brand',
            'tag'
        ]

    def filter_support_comma_separated(self, filter_query, queryset, *args):
        query_param = args[0]
        filter_kwargs = { filter_query: query_param }
        if ',' in query_param:
            params = query_param.split(',')
            for param in params:
                filter_kwargs[filter_query] = param
                queryset = queryset.filter(**filter_kwargs)
        else:
            queryset = queryset.filter(**filter_kwargs)
        return queryset

    def filter_category_title(self, queryset, value, *args, **kwargs):
        filter_query = 'category__slug__icontains'
        queryset = self.filter_support_comma_separated(filter_query, queryset, *args)
        return queryset

    def filter_color_title(self, queryset, value, *args, **kwargs):
        filter_query = 'packs__color__title__icontains'
        queryset = self.filter_support_comma_separated(filter_query, queryset, *args)
        return queryset

    def filter_brand_title(self, queryset, value, *args, **kwargs):
        filter_query = 'brand__title'
        queryset = self.filter_support_comma_separated(filter_query, queryset, *args)
        return queryset

    def filter_tag_title(self, queryset, value, *args, **kwargs):
        filter_query = 'tags__title'
        queryset = self.filter_support_comma_separated(filter_query, queryset, *args)
        return queryset

    def filter_in_stock_availability(self, queryset, value, *args, **kwargs):
        return queryset.exclude(count_stock=0)