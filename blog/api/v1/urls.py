from django.urls import include, path, re_path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework import routers
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from .views import *

router = routers.SimpleRouter()
router.register(r'post_relation', UserPostRelationView)
router.register(r'bikes', BikesViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),

    path('v1/drf-auth/', include('rest_framework.urls')),
    path('v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("v1/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("v1/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

]
