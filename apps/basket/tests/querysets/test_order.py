from collections import Counter
from django.test import TestCase

from warehouse.repository.generator_layer import WarehouseDataGenerator
from basket.repository.generator_layer import BasketDataGenerator
from account.repository.generator_layer import AccountDataGenerator
from logistic.repository.generator_layer import LogisticDataGenerator
from voucher.repository.generator_layer import VoucherDataGenerator

from painless.utils.decorators import (
    disable_logging,
    test_time_upper_limit,
)

from basket.models import Order
from warehouse.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderQuerysetManager(TestCase):
    TOTAL_PRODUCTS = 100

    @classmethod
    @disable_logging
    def setUpClass(cls) -> None:
        super(OrderQuerysetManager, cls).setUpClass()

        # Account Data Generator
        account_dgl = AccountDataGenerator()
        account_dgl.create_user(10)
        account_dgl.create_profile()
        # Warehouse Data Generator
        warehouse_dgl = WarehouseDataGenerator()
        brands = warehouse_dgl.create_brands(5)
        categories = warehouse_dgl.create_categories(100)
        category = warehouse_dgl.create_categories(total=100, is_physical=True)
        colors = warehouse_dgl.create_colors(10)
        warranties = warehouse_dgl.create_warranties(10)
        tags = warehouse_dgl.create_tags(5)
        products = warehouse_dgl.create_products(brands, categories, tags, 10)
        product = warehouse_dgl.create_products(brands, category, tags, 10)
        warehouse_dgl.create_physical_info()
        warehouse_dgl.create_packs(colors, warranties, products, 50)
        warehouse_dgl.create_packs(colors, warranties, product, 50)
        warehouse_dgl.create_expenses()
        warehouse_dgl.create_product_gallery(
            products,
            lower_boundary=3,
            upper_boundary=5
        )

        # Voucher Data Generator
        voucher_dgl = VoucherDataGenerator()
        vouchers = voucher_dgl.create_voucher(10)
        voucher_dgl.create_single_use_voucher()
        voucher_ranges = voucher_dgl.create_voucher_range()
        voucher_dgl.create_many_to_many_data(
            voucher_ranges=voucher_ranges,
            vouchers=vouchers,
        )

        # Logistic Data Generator
        logistic_dgl = LogisticDataGenerator()
        logistic_dgl.create_address(5)
        logistics = logistic_dgl.create_logistic(total=100)
        logistic_dgl.create_address()
        logistic_dgl.create_delivery_time_range(
            logistics=logistics, total=100)
        logistic_dgl.create_logistic_distance_range(
            logistics=logistics, total=100)
        logistic_dgl.create_logistic_weight_range(
            logistics=logistics, total=100)
        logistic_dgl.create_logistic_cost_range(
            logistics=logistics, total=100)

        # Basket Data Generator
        basket_dgl = BasketDataGenerator()
        basket_dgl.create_cart()
        basket_dgl.create_pack_cart()
        basket_dgl.create_order_addresses(10)
        orders = basket_dgl.create_orders()
        basket_dgl.create_pack_order(orders)
        basket_dgl.create_refund()

    @test_time_upper_limit(0.1)
    def test_queryset_get_all_orders_for_given_product(self):
        prod_sample = Product.objects.first()
        actual = set(Order.dal.get_all_orders_for_given_product(prod_sample))
        expected = []
        for pack in prod_sample.packs.all():
            for order in pack.orders.all():
                expected.append(order)

        self.assertEqual(
            Counter(actual),
            Counter(set(expected)),
            msg=(f"Actual list of orders for product is `{actual}` "
                 f"but expected is `{expected}`.")
        )

    def test_queryset_get_all_orders_with_status_count(self):
        user = User.objects.first()
        order_dal = Order.dal.get_all_orders_with_status_count(user)
        actual = order_dal

        orders_obj = Order.objects.filter(user=user)
        quantity = {
            'shipped': 0,
            'waiting': 0,
            'expiring': 0,
            'cancelled': 0,
            'delivered': 0,
            'completed': 0,
            'processing': 0,
            'orders': orders_obj.count()
        }

        for order in orders_obj:
            quantity[order.status] += 1

        expected = dict()
        for k in quantity.keys():
            new_key = k + '_num'
            expected[new_key] = quantity[k]

        self.assertDictEqual(
            actual,
            expected,
            msg=f"actual status number for given user is{actual}"
                f" but expected is {expected}"
        )

    def test_queryset_get_all_orders_of_user(self):
        user = User.objects.prefetch_related('orders').first()
        order_dal = Order.dal.get_all_orders_of_user(user)
        actual = order_dal

        with self.assertNumQueries(0):
            expected = [
                order
                for order in user.orders.all()
            ]

        self.assertQuerysetEqual(
            actual,
            expected,
            ordered=False,
            msg=f"actual orders for given user are {actual}"
                f" but expected are {expected}"
        )

    def test_queryset_get_order_total_quantity(self):
        orders_dal = Order.dal.get_order_total_quantity()
        order = orders_dal.first()
        actual = order.quantity

        order_obj = Order.objects.prefetch_related('pack_orders')\
            .get(id=order.id)
        expected = sum([
            pack_ord.quantity
            for pack_ord in order_obj.pack_orders.all()
        ])

        self.assertEqual(
            actual,
            expected,
            msg=f"Actual sum of quantity is {actual}"
                f" but expected is {expected}"
        )

    def test_queryset_get_order_by_transaction(self):
        transaction_num = Order.objects.last().transaction_number
        order_dal = Order.dal.get_order_by_transaction(transaction_num)
        actual = order_dal

        orders_obj = Order.objects.all()
        expected = [
            order
            for order in orders_obj
            if order.transaction_number == transaction_num
        ][0]

        self.assertEqual(
            actual,
            expected,
            msg=f"actual orders for given transaction_number is {actual}"
                f" but expected is {expected}"
        )

    def test_queryset_get_order_related(self):
        expected_hits = 3
        with self.assertNumQueries(expected_hits):
            orders_dal = Order.dal.get_order_related()

            for order in orders_dal:
                logistic = order.logistic
                order_address = order.order_address
                for pack in order.packs.all():
                    pack = pack.id
                for voucher in order.vouchers.all():
                    voucher = voucher.id
                    return (logistic, order_address, voucher, pack)

    def test_queryset_get_order_detail(self):
        transaction_num = Order.objects.last().transaction_number
        order_dal = Order.dal.get_order_detail(transaction_num).first()
        actual = [
            order_dal.phone_number,
            order_dal.receiver_phone_number,
            order_dal.logistic_date,
        ]

        order_obj = Order.objects\
            .select_related(
                'user',
                'logistic',
                'order_address',
            ).get(transaction_number=transaction_num)

        expected = [
            order_obj.user.phone_number,
            order_obj.order_address.receiver_phone_number,
            order_obj.logistic.delivery_time
            if order_obj.status == 'delivered' else None,
        ]

        self.assertListEqual(
            actual,
            expected,
            msg=f"actual order detail is {actual} "
                f"but expected is {expected}"
        )

    def test_queryset_get_all_pack_orders(self):
        order = Order.objects.first()
        expected_hits = 5
        with self.assertNumQueries(expected_hits):

            order_dal = Order.dal.get_all_pack_orders(order)
            for pack_order in order_dal:
                pack = pack_order.pack
                color = pack_order.pack.color
                product = pack_order.pack.product
                expense = pack_order.pack.expense
            return (color, product, expense, pack)

    def test_queryset_get_all_virtual_downloadable_products(self):
        user = User.objects.last()
        orders_dal = Order.dal.get_all_virtual_downloadable_products(user)
        actual = orders_dal

        orders_obj = Order.objects.filter(user=user)\
            .prefetch_related('pack_orders__pack__product__category')

        expected_hits = 5
        with self.assertNumQueries(expected_hits):
            expected = [
                order
                for order in orders_obj
                for pack_order in order.pack_orders.all()
                if (
                    pack_order.pack.product.category.is_virtual
                    and
                    pack_order.pack.product.category.is_downloadable
                )
            ]

        self.assertQuerysetEqual(
            actual,
            expected,
            ordered=False,
            msg=f"actual orders for given user are `{actual}`"
                f"but expected are `{expected}`"
        )
