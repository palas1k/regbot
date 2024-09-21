import logging

from django.apps import AppConfig
from django.conf import settings

from regbot.telegram.bot import bot_lifespan

logger = logging.getLogger(__name__)


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "regbot"

    def ready(self):
        if settings.BOT_MAIN:
            from django_asgi_lifespan.register import register_lifespan_manager

            register_lifespan_manager(
                context_manager=bot_lifespan,
            )
