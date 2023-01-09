from django.db.models import Prefetch

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin
)

from rest_framework.renderers import (
    JSONOpenAPIRenderer,
    BrowsableAPIRenderer,
)

from painless.api.renderers import DataStatusMessage_Renderer

from warehouse.models import Brand, Product
from warehouse.api.serializers import (
    BrandSerializer,
    ProductSerializer
)


class BrandViewSet(
        ListModelMixin,
        RetrieveModelMixin,
        GenericViewSet):
    """
    Sepehr Write a document here for tutorial!
    """
    # Stick to Serializer
    queryset = Brand.dal.get_api_related_products()
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    # Data Representation
    renderer_classes = [
        BrowsableAPIRenderer,
        JSONOpenAPIRenderer
    ]

    # Filter | Search | Order
    filter_backends = [
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend
    ]
    filterset_fields = []
    search_fields = [
        'title',
    ]
    ordering_fields = [
        'title',
        'created',
        'total_active_products'
    ]
