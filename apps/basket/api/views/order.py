from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings

from rest_framework.viewsets import GenericViewSet
from rest_framework import exceptions
from rest_framework import status
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin
)
from rest_framework.renderers import (
    JSONOpenAPIRenderer,
    BrowsableAPIRenderer,
)

from django_filters.rest_framework import DjangoFilterBackend

from basket.models import Order
from basket.api.serializers import (
    OrderSerializer,
)


class OrderViewSet(
        ListModelMixin,
        RetrieveModelMixin,
        GenericViewSet):
    permission_classes = (
        IsAuthenticatedOrReadOnly,
    )
    serializer_class = OrderSerializer
    def get_queryset(self):
        queryset = Order.dal\
            .get_order_related()\
            .get_all_orders_of_user(self.request.user)\
            .get_order_total_quantity()
        return queryset