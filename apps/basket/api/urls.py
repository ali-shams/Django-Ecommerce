from rest_framework import routers
from .views import (
    CartViewSet,
    OrderViewSet
)

router = routers.DefaultRouter()
router.register(r'carts', CartViewSet)
router.register(r'orders', OrderViewSet, basename='orders')
urlpatterns = router.urls

