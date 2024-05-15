from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from bike_app.views import *

urlpatterns = [
    path("admin/", admin.site.urls),

    path('captcha/', include('captcha.urls')),
    path('', include('bike_app.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('api/', include('api.v1.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
]
if settings.DEBUG:
    urlpatterns = [
                      path("__debug__/", include("debug_toolbar.urls")),
                  ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = page_not_found
admin.site.site_header = "Панель администрирования"
admin.site.index_title = "Посты"
