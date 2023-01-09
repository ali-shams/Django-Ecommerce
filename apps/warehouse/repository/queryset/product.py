from typing import (Optional,
                    Union,
                    Any)
from datetime import datetime

from django.apps import apps
from django.db.models import (
    QuerySet, Subquery, OuterRef,
    Prefetch, Count, When, Case,
    Func, Sum, Max, Min, Avg, F,
    Q, ImageField, BooleanField,
    DateTimeField
)
from django.db.models.functions import Coalesce

from painless.models.fields import MoneyRialCurrencyOutput


class ReportQuerySet(QuerySet):

    def report_products_with_one_default_pack(self):
        """All products that have exactly one default pack"""
        qs = self.annotate(
            total_defaults=Count('packs__is_default',
                                 filter=Q(packs__is_default=True))) \
            .filter(total_defaults__exact=1).count()
        return qs

    def report_products_with_no_pack(self):
        """get products without packs"""
        return self.prefetch_related('packs').filter(packs__isnull=True)

    def get_average_packs_per_product(self):
        """Average of packs per product

        Get average with `pack_avg` attribute on Queryset
        """
        return self.annotate(pack_count=Count('packs')).aggregate(
            pack_avg=Avg('pack_count'))

    def get_average_of_product_costs(self):
        """Average of product price

        Get average with `avg_cost` attribute on Queryset
        """
        return self.annotate(avg_cost=Avg('packs__expense__price'))


class AnnotationQuerySet(QuerySet):

    def get_queryset_of_packs_per_product(self, product_title=None):
        """Number of packs per product

        Get all products with `total_packs` attribute on Queryset
        """
        if product_title:
            qs = self.filter(title__contains=product_title) \
                .annotate(total_packs=Count('packs'))
        else:
            qs = self.annotate(total_packs=Count('packs'))
        return qs

    def get_product_with_category_and_packs(self, is_active=None):
        '''
        Getting all products with categories and all packs
        Get attribute with `product_category` attribute on Queryset
        '''
        qs = self.annotate(
            product_category=F('category__title')
        ).prefetch_related('packs').select_related('category')

        if is_active:
            qs = qs.filter(packs__is_active=is_active).distinct()
        return qs

    def get_product_with_most_or_least_tags(self, is_most):
        """
        The most used tag used in products
        Get number of tag with `tag_count` attribute on Queryset
        """
        # TODO: Discussion with arash for qs.first()
        is_most_tags = '-tag_count' if is_most else 'tag_count'
        qs = self.annotate(tag_count=Count('tags')).order_by(is_most_tags)
        return qs.filter(tag_count=qs.first().tag_count)

    def get_average_of_tags_per_product(self):
        """Average of tags per product

        Get average with `tag_avg` attribute on Queryset
        """
        return self.annotate(tag_count=Count('tags')).aggregate(
            tag_avg=Avg('tag_count'))

    def get_most_expensive_or_cheapest_product(self, is_expensive):
        """
        Most expensive pack of product
        ----
        Get most expensive price with `maximum_price` attribute on Queryset
        """
        if is_expensive:
            qs = self.annotate(max_price=Max('packs__expense__price'))
        else:
            qs = self.annotate(min_price=Min('packs__expense__price'))
        return qs

    def get_actual_count_of_stock(self):
        """
        Actual number of stock available
        ----
        Get number with `stock_count` attribute on Queryset
        """
        return self.annotate(
            stock_count=Sum('packs__expense__actual_count_stock'))

    def get_queryset_of_product_with_the_least_or_most_purchase(self, is_the_most: bool = True):
        """
        The list of the least or most purchased products
        ----
        Get quantity with `product_quantity` attribute on Queryset

        PARAMS
        ------
        `preferred_order` : bool
            default value is True
        """
        # TODO: Add most_purchase as well.
        if is_the_most:
            qs = self.annotate(
                product_quantity=Coalesce(Sum('packs__pack_orders__quantity'), 0)
            ).order_by('-product_quantity')
        else:
            qs = self.annotate(
                product_quantity=Coalesce(Sum('packs__pack_orders__quantity'), 0)
            ).order_by('product_quantity')
        return qs

    def get_default_pack_price(self):
        """get default pack price per product"""
        currency_rate = 300_000  # Rial
        default_pack_price_query = Case(
            When(Q(packs__expense__price_currency='R'),
                 then=F('packs__expense__price')),
            When(Q(packs__expense__price_currency='T'),
                 then=F('packs__expense__price') * 10),
            When(Q(packs__expense__price_currency='USD'),
                 then=F('packs__expense__price') * currency_rate),
            output_field=MoneyRialCurrencyOutput()
        )
        return self.get_default_pack() \
            .annotate(default_pack_price=default_pack_price_query,
                      default_pack_price_currency=F('packs__expense__price_currency'),
                      pack_sku=F('packs__sku'))  # noqa

    def get_number_of_tags_per_product(self):
        """ return sum of tags used per products"""
        return self.annotate(tag_count_per_product=Count('tags'))

    def get_product_sold_count(self):
        """
        Get the quantity of all packs sold for each product in
        `product_sold_count` attribute.
        """
        Pack = apps.get_model('warehouse', 'Pack')
        pack_query = Pack.dal.filter(product__id=OuterRef('pk')) \
            .values('id') \
            .annotate(
            packs_sold_amount=Func('pack_orders__quantity', function='Sum')
        ).values('packs_sold_amount')
        return self.annotate(product_sold_count=Subquery(pack_query))

    def get_the_product_based_on_the_packs_sold_in_order(self):
        """
        The product packs are sorted based on the best sellers
        Get sum of quantity with `quantity_order` attribute on Queryset
        """
        Pack = apps.get_model('warehouse', 'Pack')
        return self.prefetch_related(
            Prefetch(
                'packs', Pack.objects.annotate(quantity_order=Coalesce(Sum('pack_orders__quantity'), 0)).order_by(
                    '-quantity_order')
            ))

    def get_total_active_packs(self):
        """get total active packs per product"""
        return self.annotate(
            total_active_packs=Coalesce(Count('packs', filter=Q(packs__is_active=True)), None))

    def get_title_of_default_pack_warranty(self):
        """get title of default pack warranty"""
        return self.get_default_pack() \
            .annotate(title_of_default_pack_warranty=Coalesce(F('packs__warranty__title'), None))

    def get_total_packs_in_orders(self):
        """get all packs submitted in each order"""
        return self.annotate(total_packs_in_orders=
                             Coalesce(Count('packs__pack_orders__pack_id'), 0))

    def get_number_sold_per_product_per_country(self):
        """get the number of products sold per country"""
        return self.annotate(total_sold_product_per_contry=
                             Coalesce(Sum('packs__pack_orders__quantity'), 0),
                             country=F('packs__pack_orders__order__order_address__country'))

    def get_number_sold_per_product_per_country_per_province(self):
        """get the number of products sold per country, per province"""
        return self.annotate(total_sold_product_per_contry_per_province=
                             Coalesce(Sum('packs__pack_orders__quantity'), 0),
                             country=F('packs__pack_orders__order__order_address__country'),
                             province=F('packs__pack_orders__order__order_address__province'))

    def get_profit_per_product(self):
        """get profit by subtracting the cost
        from the buy price multiplied by the quantity"""
        return self.annotate(profit=Coalesce(Sum(F('packs__pack_orders__quantity') * (
                F('packs__pack_orders__cost') - F('packs__pack_orders__buy_price'))), None))

    def get_picture_choices(self):
        """get picture for product

        Get choices with (`first_pic`,`second_pic`, `other_pic`)
        attribute on Queryset
        """
        ProductGallery = apps.get_model('warehouse', 'ProductGallery')
        first_img = ProductGallery.objects \
            .filter(product_id=OuterRef('pk')) \
            .annotate(first_pic=F('picture')) \
            .filter(image_status='first') \
            .values('first_pic')
        second_img = ProductGallery.objects \
            .filter(product_id=OuterRef('pk')) \
            .annotate(second_pic=F('picture')) \
            .filter(image_status='second') \
            .values('second_pic')
        return self.prefetch_related(
            Prefetch('galleries',
                     queryset=ProductGallery.objects
                     .filter(image_status='other'),
                     to_attr='other_pic')
        ). \
            annotate(
            first_pic=Subquery(first_img, output_field=ImageField()),
            second_pic=Subquery(second_img, output_field=ImageField())
        )

    def get_default_picture(self):
        """get default picture for product

        Get default with `default_pic` attribute on Queryset
        """
        ProductGallery = apps.get_model('warehouse', 'ProductGallery')
        return self.filter(galleries__is_default=True) \
            .prefetch_related(Prefetch('galleries',
                                       queryset=ProductGallery.dal.get_default())) \
            .annotate(default_pic=F('galleries__picture'))


class BaseProductQuerySet(QuerySet):
    def get_actives(self, is_active=True):
        """Get all active/inactive products"""
        return self.filter(is_active=is_active)

    def get_vouchers(self, is_voucher_active=True):
        """Get all active/de-active vouchers on products"""
        return self.filter(is_voucher_active=is_voucher_active)

    def get_default_pack(self):
        """get default pack for product

        Get default with `pack` attribute on Queryset
        """
        Pack = apps.get_model("warehouse", "Pack")
        return self.filter(packs__is_default=True).prefetch_related(
            Prefetch(
                'packs',
                Pack.dal.get_default(is_default=True),
                to_attr='pack'
            )
        )


class ProductQuerySet(BaseProductQuerySet, AnnotationQuerySet, ReportQuerySet):

    def get_active_products_with_voucher(
            self,
            is_active=True,
            is_voucher_active=True
    ):
        """Get all active/inactive vouchers in active products"""
        return self.get_actives(is_active).get_vouchers(is_voucher_active)

    def get_active_category(self):
        """
        Get all active categories of product.
        """
        return self.select_related('category') \
            .filter(category__is_active=True)

    def get_active_packs(self):
        """
        Get active packs of a product.
        """
        return self.filter(packs__is_active=True)

    def get_related_packs(self):
        """
        Get product packs, pack color, expense, and warranty.
        """
        return self.prefetch_related('packs') \
            .prefetch_related('packs__color')

    def get_available_items(self, fields=None):
        """
        Get necessary items needed to load a product page.
        """
        if fields is None:
            fields = [
                'title',
                'sku',
                'slug',
                'description',
                'subtitle',
                'is_active',
                'is_voucher_active',
                'brand',
                'category',
                'created'
            ]
        return self.get_actives() \
            .get_active_category() \
            .select_related('brand') \
            .get_related_packs() \
            .get_active_packs() \
            .get_total_actual_count_stock_active_packs() \
            .get_default_pack_price() \
            .get_picture_choices() \
            .count_stock_products() \
            .get_total_active_packs() \
            .get_default_picture() \
            .order_by('-total_actual_count_stock') \
            .only(*fields)
