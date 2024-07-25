from rest_framework import serializers

from regbot.users.models import User


class ClientSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(min_value=1, required=True)
    balance = serializers.FloatField(min_value=0, default=0)

    class Meta:
        model = User
        fields = "__all__"
