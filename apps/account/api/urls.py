from django.urls import (
    re_path,
    include
)

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = SimpleRouter()
router.register('users', UserViewSet)

urlpatterns = router.urls

urlpatterns.extend([
    # Simple JWT
    re_path(r'jwt/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'jwt/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'jwt/verify/$', TokenVerifyView.as_view(), name='token_verify'),
    # DRF
    re_path(r'session-based/', include('rest_framework.urls')),
])
