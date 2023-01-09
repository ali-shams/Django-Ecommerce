from django.contrib.auth import get_user_model
from django.db.models import (
    DateTimeField,
    CharField,
    QuerySet,
    Count,
    Case,
    When,
    Sum,
    Q,
    F
)

from azbankgateways.models import Bank


class OrderQuerySet(QuerySet):
    def get_all_orders_with_status_count(self, user: 'User'):
        '''Get all orders with status count,
        you can get count number with:

        `orders_num`, `waiting_num`, `processing_num`,

        `delivered_num`, `shipped_num`, `expiring_num`,

        `completed_num`, `cancelled_num`
        '''
        qs = self.filter(user=user).aggregate(
            orders_num=Count('status'),
            waiting_num=Count('status', filter=Q(status='waiting')),
            processing_num=Count('status', filter=Q(status='processing')),
            delivered_num=Count('status', filter=Q(status='delivered')),
            shipped_num=Count('status', filter=Q(status='shipped')),
            expiring_num=Count('status', filter=Q(status='expiring')),
            completed_num=Count('status', filter=Q(status='completed')),
            cancelled_num=Count('status', filter=Q(status='cancelled')),
        )
        return qs

    def get_all_virtual_downloadable_products(self, user : int= None):
        '''get all orders with virtual & downloadable products'''

        qs = self.prefetch_related('pack_orders__pack__product__category')\
                    .filter(user=user).filter(
                    Q(pack_orders__pack__product__category__is_virtual=True),
                    Q(pack_orders__pack__product__category__is_downloadable=True)
                    )
        return qs

    def get_all_orders_for_given_product(self, product_title: str):
        """
        get all the orders for given product.

        PARAMS
        -----
        product_title: str:
            title of target product we want orders for.
        """
        return self.filter(packs__product__title=product_title)

    def get_all_orders_of_user(self, user):
        """
        Gets all the orders of given user.
        """
        return self.filter(user=user)

    def get_order_total_quantity(self):
        """
        Annotates quantity which is the count of all packs in the order.
        stores it in `quantity` attribute.
        """
        return self.prefetch_related('pack_orders').\
            annotate(quantity=Sum('pack_orders__quantity'))

    def get_order_by_transaction(self, transaction_number: int):
        """
        returns an order matching given transaction number
        """
        return self.get(transaction_number=transaction_number)

    def get_order_related(self):
        """ get all the order related """
        return self\
                .select_related('logistic', 'order_address')\
                .prefetch_related('vouchers', 'packs')
    
    def get_order_detail(self, transaction_number: int):
        """
        get details of an order by transaction number
        you can get querysets with:
        user phone number : 'phone_number'
        receiver phone number : 'receiver_phone_number'
        logistic date : 'logistic_date'
        """

        delivery_time = Case(
            When(Q(status__iexact='delivered'),
            then=F('logistic__delivery_time')
            ),
            default= None,
            output_field=CharField()
        )
        return self.filter(transaction_number=transaction_number)\
            .get_order_related()\
            .annotate(
                phone_number=F('user__phone_number'),
                receiver_phone_number=F('order_address__receiver_phone_number'),
                logistic_date=delivery_time
                )

    def get_order_with_bank_record(self, transaction_number: str):
        order = self.get(transaction_number=transaction_number)
        bank_record = Bank.objects.get(tracking_code=transaction_number)

        return order, bank_record

    def get_all_pack_orders(self, order):
        return order.pack_orders.prefetch_related(
            'pack__expense',
            'pack__product',
            'pack__color'
        )
