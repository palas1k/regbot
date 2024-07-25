from django_filters import FilterSet
from regbot.users.models import User


class ClientFilterSet(FilterSet):
    class Meta:
        model = User
        fields = (
            "telegram_id",
            "username",
            # "subscription_type",
            "subscription_expr",
            "balance",
        )
