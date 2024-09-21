import asyncio
import logging
import threading
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from django.conf import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def bot_lifespan():
    from regbot.telegram.routers.main import router as main_router
    from regbot.telegram.dialogs.main import main_window
    from regbot.telegram.dialogs.crud_reg import main_window as crud_main_window

    storage = MemoryStorage()

    bot = Bot(settings.TELEGRAM_TOKEN)
    dp = Dispatcher(storage=storage)

    setup_dialogs(dp)
    dp.include_routers(main_router, main_window, crud_main_window)

    logger.warning("Initializing bot...")

    async def start_bot():
        logger.warning("Starting polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            handle_signals=False,
        )

    if settings.BOT_USE_POLLING:
        threading.Thread(daemon=True, target=asyncio.run, args=(start_bot(),)).start()
        yield {}
    else:
        logger.warning("Setting up webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(settings.WEBHOOK_URL)
        yield {
            "dp": dp,
            "bot": bot,
        }

    await bot.close()
