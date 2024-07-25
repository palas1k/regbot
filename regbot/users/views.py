# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from regbot.users import filters, serializers
from regbot.users.models import SubscriptionType, User


class SubscriptionTypeViewSet(ModelViewSet):
    queryset = SubscriptionType.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.soft_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientViewSet(ModelViewSet):
    queryset = User.objects.all()
    filterset_class = filters.ClientFilterSet
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClientSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.soft_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
