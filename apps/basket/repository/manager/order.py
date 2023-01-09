from django.db.models import Manager

from basket.repository.queryset import OrderQuerySet


class OrderDataAccessLayerManager(Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def get_all_orders_with_status_count(self, user: 'User'):
        '''Get all orders with status count,
        you can get count number with:

        `orders_num`, `waiting_num`, `processing_num`,

        `delivered_num`, `shipped_num`, `expiring_num`,

        `completed_num`, `cancelled_num`
        '''
        return self.get_queryset().get_all_orders_with_status_count(user)

    def get_all_virtual_downloadable_products(self, user: 'User'=None):
        '''get all orders with virtual & downloadable products
        '''
        return self.get_queryset().get_all_virtual_downloadable_products(user)

    def get_all_orders_for_given_product(self, product_title: str):
        """
        get all the orders for given product.

        PARAMS
        -----
        product_title: str:
            title of target product we want orders for.
        """
        return self.get_queryset().get_all_orders_for_given_product(product_title)

    def get_all_orders_of_user(self, user):
        """
        Gets all the orders of given user
        """
        return self.get_queryset().get_all_orders_of_user(user)

    def get_order_total_quantity(self):
        """
        Annotates quantity which is the count of all packs in the order.
        stores it in `quantity` attribute.
        """
        return self.get_queryset().get_order_total_quantity()

    def get_order_by_transaction(self, transaction_number: str):
        """
        returns an order matching given transaction number
        """
        return self.get_queryset().get_order_by_transaction(transaction_number)

    def get_order_related(self):
        """ get all the order related """
        return self.get_queryset().get_order_related()

    def get_order_detail(self, transaction_number: str):
        """
        get details of an order by transaction number
        you can get querysets with:
        user phone number : 'phone_number'
        receiver phone number : 'receiver_phone_number'
        logistic date : 'logistic_date'
        """
        return self.get_queryset().get_order_detail(transaction_number)

    def get_order_with_bank_record(self, transaction_number: str):
        """
        get the order and bank record with related transaction number
        bank record is from as_bank_gateway package
        """
        return self.get_queryset().get_order_with_bank_record(transaction_number=transaction_number)

    def get_all_pack_orders_with_total_order_cost(self, order):
        return self.get_queryset().get_all_pack_orders(order)\
            .annotate_cost_each_pack_cart_with_total_cart_cost()

    def get_all_pack_orders(self, order):
        return self.get_queryset().get_all_pack_orders(order)
