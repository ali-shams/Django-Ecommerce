import logging
from django.db import transaction

from django.apps import apps
from django.db.models import F
from django.db.models import Manager
from warehouse.helper.exceptions import (
    CategoryNotActive,
    ProductNotActive,
    PackNotAvailable,
    OutOfStock,
    PackDoesNotExist,
    PackOutOfStock,
    InvalidPackStockValue,
    PackNotActive,
    UnexpectedBehavior
)

logger = logging.getLogger(__name__)


class ExpenseBusinessLogicLayer(Manager):
    """
    handles functions affecting Expense model, such as adding or removing
    something to it or checking the state of it.
    """
    def update_count_stock(self,
                        pack_sku,
                        quantity: int,
                        increase: bool) -> int:
        """
        update `count_stock` by quantity, after user purchase .
        Increase can be `True` or `False`.
        """
        with transaction.atomic():

            expense = self.get(pack__sku=pack_sku)
            pack_count_stock = expense.count_stock

            if increase and quantity >= 0:
                self.filter(pack__sku=pack_sku)\
                    .select_for_update()\
                    .update(count_stock=F('count_stock') + quantity)
                logger.info(f"the count stock of {pack_sku} is increased")

            elif pack_count_stock - quantity >= 1 and not increase and quantity >= 0:
                self.filter(pack__sku=pack_sku)\
                    .select_for_update()\
                    .update(count_stock=F('count_stock') - quantity)
                logger.info(f"the count stock of {pack_sku} is decreased")

            elif pack_count_stock - quantity == 0 and not increase and quantity >= 0:
                self.filter(pack__sku=pack_sku)\
                    .select_for_update()\
                    .update(count_stock=F('count_stock') - quantity)
                logger.warning(f"the count stock of {pack_sku} is zero")

            elif pack_count_stock - quantity < 0 and not increase and quantity >= 0:
                logger.warning(f"the count_stock of {pack_sku} is zero")
                raise PackOutOfStock(f"Insufficient stock for pack {pack_sku}")

            else :
                logger.error(
                    f"Unexpected behavior from {self.__class__.__name__}"
                    f" in update_count_stock method"
                    )
                raise UnexpectedBehavior(
                    f"Unexpected behavior from {self.__class__.__name__}"
                    )

            return self.get(pack__sku=pack_sku).count_stock

    def update_actual_count_stock(self,
                                  pack_sku,
                                  quantity: int,
                                  increase: bool):
        """
        update `actual_count_stock` by quantity, after user purchase .
        Increase can be `True` or `False`.
        """
        with transaction.atomic():

            expense = self.get(pack__sku=pack_sku)
            pack_actual_count_stock = expense.actual_count_stock

            if increase and quantity >= 0:
                self.filter(pack__sku=pack_sku)\
                    .select_for_update()\
                    .update(actual_count_stock=F('actual_count_stock') + quantity)
                logger.info(f"the actual count stock of {pack_sku} is increased")

            elif pack_actual_count_stock - quantity >= 1 and not increase and quantity >= 0:
                self.filter(pack__sku=pack_sku)\
                    .select_for_update()\
                    .update(actual_count_stock=F('actual_count_stock') - quantity)
                logger.info(f"the actual count stock of {pack_sku} is decreased")

            elif pack_actual_count_stock - quantity == 0 and not increase and quantity >= 0:
                logger.warning(f"the actual count stock of {pack_sku} is zero")
                self.filter(pack__sku=pack_sku)\
                    .select_for_update()\
                    .update(actual_count_stock=F('actual_count_stock') - quantity)
                logger.warning(f"the actual count stock of {pack_sku} is zero")

            elif pack_actual_count_stock - quantity < 0 and not increase:
                try:
                    raise PackOutOfStock(f"Insufficient stock for pack {pack_sku}")
                except PackOutOfStock as e:
                    logger.error(e)
                    raise PackOutOfStock(f"Insufficient stock for pack {pack_sku}")

            else :
                logger.error(
                    f"Unexpected behavior from {self.__class__.__name__}"
                    f" in update_actual_count_stock method"
                    )
                raise UnexpectedBehavior(
                    f"Unexpected behavior from {self.__class__.__name__}"
                    )

            return self.get(pack__sku=pack_sku).actual_count_stock


class PackBusinessLogicLayer(Manager):
    """
    handles functions affecting Pack model, such as adding or removing
    something to it or checking the state of it.
    """
    def is_available(
            self,
            pack_sku: 'Pack',
    ) -> bool:
        """
        Checks if:
            1- parent category of pack and all their parents are active.
            2- the product pack belongs to is active.
            3- the brand the pack's product belongs to is active. (Not Implemented)
        if any of these conditions are not met, an exception is raised.
        returns the pack if conditions are met.
        """
        pack = self.get(sku=pack_sku)
        categories = pack.product.category.get_family()
        for category in categories:
            try:
                if not category.is_active:
                    raise CategoryNotActive(f'Given pack with sku: {pack.sku} '
                                            f'cannot be added to the cart')
            except CategoryNotActive as e:
                logger.error(e)
                raise CategoryNotActive(f'Given pack with sku: {pack.sku} '
                                        f'cannot be added to the cart')

        if not pack.is_active:
            try: 
                raise PackNotActive(f"Pack {pack.sku} isn't available")
            except PackNotActive as e:
                logger.error(e)
                raise PackNotActive(f"Pack {pack.sku} isn't available")

        if not pack.product.is_active:
            try:
                raise ProductNotActive(f'Given pack with sku: {pack.sku} '
                                       f'cannot be added to the cart')
            except ProductNotActive as e:
                logger.error(e)
                raise ProductNotActive(f'Given pack with sku: {pack.sku} '
                                       f'cannot be added to the cart')
        # elif not pack.product.brand.is_active:
        #     raise Exception
        else:
            return True

    def is_pack_in_stock(self,
                         pack_sku: 'Pack',
                         quantity: int) -> bool:
        """
        Checks if:
            1- pack either not out of stock or is suppliable.
            2- pack stock is higher than given quantity.
        if any of these conditions are not met, an exception is raised.
        returns the pack if conditions are met.
        """
        pack = self.get(sku=pack_sku)
        if not pack.expense.count_stock > 0 :
            raise PackNotAvailable(f"Insufficient stock for pack {pack.sku}")
        elif not pack.expense.is_suppliable:
            raise PackNotAvailable(f"Insufficient stock for pack {pack.sku}")
        elif not pack.is_active:
            raise PackNotAvailable(f"Insufficient stock for pack {pack.sku}")
        elif not pack.expense.count_stock >= quantity:
            raise OutOfStock(f"Insufficient stock for pack {pack.sku}")
        else:
            return True

    def is_actual_count_stock_gte_stock(self,
                                        pack_sku,
                                        ) -> 'Pack':
        """"to check whether the actual count stock
        of a given pack is greater than
        or equal to the count stock"""
        pack = self.get(sku=pack_sku)
        if not pack.expense.actual_count_stock >= pack.expense.count_stock:
            raise InvalidPackStockValue(f'stock amount for pack {pack.sku} '
                                        f'is invalid.')
        else:
            return True

    @staticmethod
    def make_pack_and_all_its_categories_active(pack: 'Pack',
                                                quantity: int = None) -> 'Pack':
        """
        Makes the pack and its product and all categories of its product active.
        """
        Category = apps.get_model('warehouse.category')
        categories = pack.product.category.get_family()
        if not pack.product.is_active:
            pack.product.is_active = True
        if not (pack.expense.count_stock > 0 or
                pack.expense.is_suppliable):
            pack.expense.is_suppliable = True
        if not pack.is_active:
            pack.is_active = True
        if quantity is not None:
            if not pack.expense.count_stock >= quantity:
                pack.expense.count_stock = quantity + 1
        pack.save()
        for category in categories:
            if not category.is_active:
                Category.objects.filter(id=category.id).update(is_active=True)
        return pack


class BrandBusinessLogicLayer(Manager):
    """
    handles functions affecting Brand model, such as adding or removing
    something to it or checking the state of it.
    """
    def update_product_is_active(self,
                                 brand_slug: 'Brand',
                                 is_active: bool) -> None:
        """
        sets the `is_active `status of all products belonging to the given
        brand to given bool.
        """
        with transaction.atomic():
            brand = self.get(slug=brand_slug)
            Product = apps.get_model('warehouse.product')
            Product.bll.select_for_update()\
                .filter(brand=brand)\
                .update(is_active=is_active)
            logger.info(f" all products are activated by given brand `{brand.title}`")


class ProductBusinessLogicLayer(Manager):
    """
    handles functions affecting Product model, such as adding or removing
    something to it or checking the state of it.
    """
    def update_pack_is_active(self,
                              product_sku: 'Product',
                              is_active: bool) -> None:
        """
        sets the `is_active `status of all packs belonging to the given
        product to given bool.
        """
        with transaction.atomic():
            Pack = apps.get_model('warehouse.pack')
            product = self.get(sku=product_sku)
            Pack.bll.select_for_update()\
                .filter(product=product)\
                .update(is_active=is_active)
            logger.info(f" all packs are activated by given product `{product.title}`")
