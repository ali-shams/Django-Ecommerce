import random
import mimesis

from django.test import (TestCase,
                         TransactionTestCase)

from painless.utils.decorators import (
    disable_logging,
    test_time_upper_limit,
)

from warehouse.repository.generator_layer import WarehouseDataGenerator
from basket.repository.generator_layer import BasketDataGenerator
from account.repository.generator_layer import AccountDataGenerator
from voucher.repository.generator_layer import VoucherDataGenerator
from logistic.repository.generator_layer import LogisticDataGenerator

from basket.helper.exceptions import FailedAddToCart

from basket.services import PrePaymentServices

from warehouse.models import (Pack,
                              Product)
from basket.models import (PackCart,
                           Cart,
                           Order,
                           OrderAddress)
from account.models import User
from voucher.models import Voucher
from logistic.models import Logistic


class PrePaymentServicesTest(TestCase):
    @classmethod
    @disable_logging
    def setUpClass(cls) -> None:
        super(PrePaymentServicesTest, cls).setUpClass()

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
        delivery_time_range = logistic_dgl.create_delivery_time_range(logistics=logistics, total=100)
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
    def test_add_pack_to_cart(self):
        """
        Test to see if invalid packs raise exception.
        valid packs are already tested in bll and won't be tested again.
        """
        quantity = random.randint(1, 100)
        cart = Cart.objects.first()
        products = Product.objects.select_related('category')

        out_of_stock_pack = products[0].packs.first()
        out_of_stock_pack.expense.count_stock = 0
        out_of_stock_pack.save()

        inactive_pack = products[1].packs.first()
        inactive_pack.is_active = False
        inactive_pack.save()

        pack_with_inactive_product = products[2].packs.first()
        pack_with_inactive_product.product.is_active = False
        pack_with_inactive_product.save()

        pack_with_inactive_category = products[3].packs.first()
        pack_with_inactive_category.product.category.is_active = False
        pack_with_inactive_category.save()

        with self.assertRaises(FailedAddToCart):
            PrePaymentServices().add_pack_to_cart(cart, out_of_stock_pack, quantity)
        # TODO: This should raise FailedAddToCart with inactive_pack
        # with self.assertRaises(FailedAddToCart):
        #     PrePaymentServices().add_pack_to_cart(cart, inactive_pack, quantity)
        with self.assertRaises(FailedAddToCart):
            PrePaymentServices().add_pack_to_cart(cart, pack_with_inactive_product, quantity)
        # TODO: This should raise FailedAddToCart with pack_with_inactive_category
        # with self.assertRaises(FailedAddToCart):
        #     PrePaymentServices().add_pack_to_cart(cart, pack_with_inactive_category, quantity)


class TransactionPrePaymentServicesTest(TransactionTestCase):
    @classmethod
    @disable_logging
    def setUpClass(cls) -> None:
        super(TransactionPrePaymentServicesTest, cls).setUpClass()

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
        delivery_time_range = logistic_dgl.create_delivery_time_range(logistics=logistics, total=100)
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
