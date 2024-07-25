from rest_framework.routers import DefaultRouter

from regbot.users import views

router = DefaultRouter()


router.register(r"clients", views.ClientViewSet)
