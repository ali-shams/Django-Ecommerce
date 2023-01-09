from django.core.cache import cache

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.throttling import (
    UserRateThrottle,
    AnonRateThrottle
)
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin
)

from rest_framework.renderers import (
    BrowsableAPIRenderer,
    JSONOpenAPIRenderer
)


from warehouse.api.serializers import ProductSerializer
from warehouse.models import Product


class ProductViewSet(
        ListModelMixin,
        RetrieveModelMixin,
        GenericViewSet):
    # Stick to Serializer
    queryset = Product.dal.get_available_items()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    # Permissions
    permission_classes = (
        IsAuthenticated,
    )
    # Data Representation
    renderer_classes = (
        BrowsableAPIRenderer,
        JSONOpenAPIRenderer
    )

    # Filter | Search | Order
    filter_backends = [
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend
    ]
    filterset_fields = [
        'category',
        'packs__expense__price',
        'tags',
        'is_active',
        'brand'
    ]
    search_fields = [
        'title',
        'brand__title',
        'category__title',
    ]
    ordering_fields = [
        'title',
        'created'
    ]

    # Action
    @action(methods=['GET'], detail=False)
    def vouchers(self, request):
        queryset = cache.get('product_vouchers')
        if queryset is None:
            queryset = self.get_queryset().get_vouchers()
            cache.set('product_vouchers', queryset)

        serializer = self.get_serializer(queryset, many=True)
        # queryset=Product.objects.all()
        # START PAGINATION
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        # END PAGINATION

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
