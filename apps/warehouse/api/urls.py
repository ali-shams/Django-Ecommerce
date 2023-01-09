from rest_framework import routers
from .views import (
    ProductViewSet,
    BrandViewSet,
    CategoryViewSet,
    BrandViewSet,
    ColorViewSet,
    TagViewSet
)

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'tags', TagViewSet)
urlpatterns = router.urls

# app_name = 'api'

# urlpatterns = [
#     path('products/', ProductListAPIView.as_view()),
#     re_path(r'^products/(?P<slug>[-\w]+)/$', ProductRetrieveAPIView.as_view())

# ]

# urlpatterns = [
#     path('categories/', CategoryViewSet.as_view()),
#     # re_path(r'^categories/(?P<slug>[-\w]+)/$', BrandRetrieveAPIView.as_view())
# ]
