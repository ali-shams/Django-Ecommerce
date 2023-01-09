from django.test import TestCase
from django.test.utils import override_settings

from warehouse.models import (
    Product,
    Brand,
    Category,
    Warranty,
    Color,
    Pack,
    # Tag
)
from basket.models import (
    Order,
    OrderAddress

)
from account.models import (User,)

from painless.utils.decorators import disable_logging


@override_settings(LANGUAGE_CODE='en')
class OrderModel(TestCase):
    """
        Test the Order model's field to make sure weather we have
        an FK to the correct model, as well as the
        correct max_length on a CharField.
        --------

        - testing the magic methods: `__str__` and `__repr__`
        - testing `verbose_name` (single & plural)
    """
    @classmethod
    @disable_logging
    def setUpClass(cls):
        """creating and preparing data for testing"""

        super(OrderModel, cls).setUpClass()

        cls.brand = Brand.objects.create(
            title='example_title_for_test',
        )
        cls.category = Category.objects.create(
            title='example_category_for_test',
            is_active=True,
            is_shippable=True,
            is_color_important=True,
            is_virtual=True,
            is_downloadable=True
        )
        # cls.tags = Tags.objects.create(
        #     title = 'example_tags_for_test',
        # )
        cls.product = Product.objects.create(
            title='example_product_for_test',
            is_active=True,
            is_voucher_active=True,
            brand=cls.brand,
            category=cls.category,
            # tags = cls.tags
        )
        cls.user = User.objects.create(
            phone_number='09192305965',
            email='moan.dastar@yahoo.com',
            first_name='Mona',
            last_name='Duster',
        )
        cls.warranty = Warranty.objects.create(
            title="Hamrah_Service",
        )
        cls.color = Color.objects.create(
            title='example_color',
            hex_code='sample_hex'
        )
        cls.pack = Pack.objects.create(
            is_active=True,
            is_default=True,
            product=cls.product,
            color=cls.color,
            warranty=cls.warranty,
        )
        cls.order_address_1 = OrderAddress.objects.create(
            country='CA',
            city='Toronto',
            province='Ontario',
            postal_address='Brampton-#45 ',
            postal_code='21354548',
            receiver_first_name='Mona',
            receiver_last_name='Dastar',
            house_number=5,#
            receiver_phone_number='01245789256',
            building_unit=15,
        )
        cls.order_address_2 = OrderAddress.objects.create(
            country='US',
            city='NewYork',
            province='NewYork',
            postal_address='Beekley-#45 ',
            postal_code='847512',
            receiver_first_name='Mona',
            receiver_last_name='Lisa',
            house_number=5,  #
            receiver_phone_number='01548554555',
            building_unit=15,
        )
        cls.order1 = Order.objects.create(
            transaction_number=1499,
            status='waiting',
            total_cost=427.00,
            total_shipping_cost=98.00,
            total_discount=15.00,
            total_cost_without_discount=329.00,
            total_cost_without_discount_and_shipping=216.00,
            order_address=cls.order_address_1,
            user=cls.user
        )
        cls.order2 = Order.objects.create(
            transaction_number=300,
            status='waiting',
            total_cost=693.00,
            total_shipping_cost=119.00,
            total_discount=6.00,
            total_cost_without_discount=574.00,
            total_cost_without_discount_and_shipping=449.00,
            order_address=cls.order_address_2,
            user=cls.user
        )

    def test_str_method(self):
        """testing str method in Order Model"""

        actual = str(self.order1)
        expected = str(self.order1.id)
        self.assertEqual(
            actual,
            expected,
            msg=f"actual __str__method is `{actual}`"
            f"but expected is is `{expected}`"  # noqa
        )

    def test_repr_method(self):
        """testing repr method in Order Model"""

        actual = [self.order1, self.order2]
        expected = list(Order.objects.all())
        self.assertEqual(
            actual,
            expected,
            msg=f"Actual __repr__ method is `{actual}` "
            f"but expected is `{expected}`"  # noqa
            )

    def test_verbose_name(self):
        """testing verbose name in Order Model"""

        actual = Order._meta.verbose_name
        expected = "Order"
        self.assertEqual(
            actual,
            expected,
            msg=f"Actual __verbose_name is `{actual}` "
            f"but expected is `{expected}`"  # noqa
        )

        actual = Order._meta.verbose_name_plural
        expected = "Orders"
        self.assertEqual(
            actual,
            expected,
            msg=f"Actual __verbose_name_plural is `{actual}` "
            f"but expected is `{expected}`"  # noqa
        )
