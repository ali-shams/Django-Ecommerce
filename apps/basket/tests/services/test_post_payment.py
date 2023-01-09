import random

from django.test import TransactionTestCase

from painless.utils.decorators import (
    disable_logging,
    test_time_upper_limit,
)

from warehouse.repository.generator_layer import WarehouseDataGenerator
from basket.repository.generator_layer import BasketDataGenerator
from account.repository.generator_layer import AccountDataGenerator
from voucher.repository.generator_layer import VoucherDataGenerator
from logistic.repository.generator_layer import LogisticDataGenerator

from basket.services import PostPaymentServices

from basket.models import Order


class PostPaymentServicesTest(TransactionTestCase):
    @classmethod
    @disable_logging
    def setUpClass(cls) -> None:
        super(PostPaymentServicesTest, cls).setUpClass()

        # Account Data Generator
        account_dgl = AccountDataGenerator()
        account_dgl.create_user(10)
        account_dgl.create_profile()
        # Warehouse Data Generator
        warehouse_dgl = WarehouseDataGenerator()
        brands = warehouse_dgl.create_brands(5)
        categories = warehouse_dgl.create_categories(100)
        colors = warehouse_dgl.create_colors(10)
        warranties = warehouse_dgl.create_warranties(10)
        tags = warehouse_dgl.create_tags(5)
        products = warehouse_dgl.create_products(brands, categories, tags, 10)
        warehouse_dgl.create_physical_info()
        warehouse_dgl.create_packs(colors, warranties, products, 50)
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
        address = logistic_dgl.create_address()
        delivery_time_range = logistic_dgl.create_delivery_time_range(logistics=logistics, total=100 )
        logistic_distance_range = logistic_dgl.create_logistic_distance_range(logistics=logistics, total=100)
        logistic_weight_range = logistic_dgl.create_logistic_weight_range(logistics=logistics, total=100)
        logistic_cost_range = logistic_dgl.create_logistic_cost_range(logistics=logistics, total=100)

        # Basket Data Generator
        basket_dgl = BasketDataGenerator()
        basket_dgl.create_cart()
        basket_dgl.create_pack_cart()
        basket_dgl.create_order_addresses(10)
        orders = basket_dgl.create_orders()
        basket_dgl.create_pack_order(orders)
        basket_dgl.create_refund()

    @test_time_upper_limit(0.1)
    def test_after_successful_payment(self):
        order = random.choice(Order.objects.prefetch_related('pack_orders__pack__expense'))
        # make sure there's sufficient stock
        for pack_order in order.pack_orders.all():
            expense = pack_order.pack.expense
            expense.count_stock += pack_order.quantity + random.randint(1, 50)
            expense.actual_count_stock = expense.count_stock + random.randint(1, 10)
            pack_order.save()
        order.refresh_from_db()

        actual_actual_stock_count = [
            pack_order.pack.expense.actual_count_stock - pack_order.quantity
            for pack_order in order.pack_orders.all()
        ]
        PostPaymentServices().after_successful_payment(order)
        order.refresh_from_db()

        # test status
        expected_status = 'processing'
        actual_status = order.status
        self.assertEqual(
            actual_status,
            expected_status,
            msg=f"Actual order initial status is `{actual_status}` "
                f"but expected is `{expected_status}`"
        )

        expected_actual_stock_count = [pack_order.pack.expense.actual_count_stock
                                       for pack_order in order.pack_orders.all()]

        self.assertListEqual(
            actual_actual_stock_count,
            expected_actual_stock_count,
        )