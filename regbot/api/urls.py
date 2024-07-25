from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()


urlpatterns = [
    path("", include(router.urls)),
    path(route="healthcheck", view=views.healthcheck_view),
    path(route="webhook", view=views.webhook),
]
