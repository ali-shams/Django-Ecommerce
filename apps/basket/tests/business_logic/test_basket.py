import random

from django.test import TestCase
from warehouse.repository.generator_layer import WarehouseDataGenerator
from basket.repository.generator_layer import BasketDataGenerator
from account.repository.generator_layer import AccountDataGenerator
from voucher.repository.generator_layer import VoucherDataGenerator
from logistic.repository.generator_layer import LogisticDataGenerator
from painless.utils.decorators import (
    disable_logging,
    test_time_upper_limit,
)
from basket.models import (PackCart,
                           Cart)
from warehouse.models import (
    Pack,
    Category,
)
from basket.helper.exceptions import PackNotInPackCart
from django.core.exceptions import ObjectDoesNotExist


class BasketBusinessLogicLayer(TestCase):

    @classmethod
    @disable_logging
    def setUpClass(cls):
        super(BasketBusinessLogicLayer, cls).setUpClass()

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
    def test_get_total_price(self):
        pack_cart_sample = random.choice(PackCart.dal.all())
        expected = PackCart.bll.get_total_price(pack_cart_sample)
        pack_cart_price = pack_cart_sample.pack.expense.price.amount
        actual = pack_cart_price * pack_cart_sample.quantity

        self.assertAlmostEqual(
            actual,
            expected,
            delta=1,
            msg=f"Actual total price is `{actual}` "
                f"but expected is `{expected}`")

    @test_time_upper_limit(0.1)
    def test_get_total_buy_price(self):
        pack_cart_sample = random.choice(PackCart.dal.all())
        expected = PackCart.bll.get_total_buy_price(pack_cart_sample)
        pack_cart_buy_price = pack_cart_sample.pack.expense.buy_price.amount
        actual = pack_cart_buy_price * pack_cart_sample.quantity

        self.assertAlmostEqual(
            actual,
            expected,
            delta=1,
            msg=f"Actual total buy price is `{actual}` "
                f"but expected is `{expected}`")

    @test_time_upper_limit(0.1)
    def test_is_pack_cart_in_cart(self):
        cart_choice = random.choice(Cart.bll.all())
        pack_cart_in_cart = cart_choice.pack_carts.first()
        pack_cart_not_in_cart = PackCart.bll.exclude(cart=cart_choice).first()
        expected_true = Cart.bll.is_pack_cart_in_cart(
            cart_choice, pack_cart_in_cart)
        expected_false = Cart.bll.is_pack_cart_in_cart(
            cart_choice, pack_cart_not_in_cart)

        self.assertEqual(
            expected_true,
            True,
            msg=f"Actual `is pack cart in cart` is {False} "
                f"but expected is {expected_true}"
        )

        self.assertEqual(
            expected_false,
            False,
            msg=f"Actual `is pack cart in cart` is {True} "
                f"but expected is {expected_false}"
        )

    @test_time_upper_limit(0.1)
    def test_update_pack_cart_quantity(self):
        cart_choice = random.choice(Cart.bll.all())
        pack_cart_not_in_cart = PackCart.bll.exclude(cart=cart_choice).first()

        pack_cart_in_cart_high_quant = cart_choice.pack_carts.filter().first()
        high_quant_id = pack_cart_in_cart_high_quant.id
        # set pack_in_cart_5's quantity sth higher than 1
        quantity = random.randint(2, 10)
        PackCart.bll.filter(id=high_quant_id).update(quantity=quantity)

        pack_cart_in_cart_one_quant = cart_choice.pack_carts.filter().last()
        one_quant_id = pack_cart_in_cart_one_quant.id
        # set pack_in_cart_1's quantity to 1
        PackCart.bll.filter(id=one_quant_id).update(quantity=1)
        pack_cart_in_cart_high_quant = PackCart.bll.get(id=high_quant_id)
        Cart.bll.update_pack_cart_quantity(cart_choice,
                                           pack_cart_in_cart_high_quant,
                                           True)
        expected = quantity + 1
        actual = PackCart.bll.get(id=high_quant_id).quantity
        self.assertEqual(
            actual,
            expected,
            msg=f"Actual quantity is `{actual}` "
                f"but expected is `{expected}`"
        )
        pack_cart_in_cart_high_quant = PackCart.bll.get(id=high_quant_id)
        Cart.bll.update_pack_cart_quantity(cart_choice,
                                           pack_cart_in_cart_high_quant,
                                           False)
        expected -= 1
        actual = PackCart.bll.get(id=high_quant_id).quantity
        self.assertEqual(
            actual,
            expected,
            msg=f"Actual quantity is `{actual}` "
                f"but expected is `{expected}`"
        )
        pack_cart_in_cart_one_quant = PackCart.bll.get(id=one_quant_id)
        Cart.bll.update_pack_cart_quantity(
            cart_choice,
            pack_cart_in_cart_one_quant,
            False)
        actual_count = PackCart.bll.filter(id=one_quant_id).count()

        self.assertEqual(
            actual_count,
            0,
            msg=f"Actual count of pack_cart after deletion is `{actual_count}` "
                f"but expected is `0`"
        )

        with self.assertRaises(PackNotInPackCart):
            Cart.bll.update_pack_cart_quantity(cart_choice,
                                               pack_cart_not_in_cart,
                                               True)

    def test_add_to_order_address(self):
        NotImplemented

    def test_add_to_order(self):
        NotImplemented

    def test_add_order_many_to_many_rels(self):
        NotImplemented

    def test_add_to_pack_order(self):
        NotImplemented

    def test_add_to_refund(self):
        NotImplemented
