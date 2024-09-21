import json
import logging

from aiogram.types import Update
from django.http import HttpRequest, HttpResponse
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


async def webhook(request: HttpRequest):
    try:
        dp = request.state["dp"]
        bot = request.state["bot"]
        await dp.feed_update(
            bot,
            Update.model_validate(json.loads(request.body), context={"bot": bot}),
        )
    finally:
        logger.debug("Handled update")
    return HttpResponse(status_code=status.HTTP_200_OK)


def healthcheck_view(request):
    return Response({"status": "OK"}, status=status.HTTP_200_OK)
