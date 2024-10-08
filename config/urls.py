from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("api/v1/", include("regbot.api.urls"), name="api"),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
