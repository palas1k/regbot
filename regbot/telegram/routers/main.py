import logging

from aiogram import Router
from aiogram.filters import (
    CommandStart,
    PROMOTED_TRANSITION,
)
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from regbot.telegram.dialogs.main import MainStateGroup

logger = logging.getLogger(__name__)
router = Router()
UNPROMOTED_TRANSITION = ~PROMOTED_TRANSITION


@router.message(CommandStart())
async def start_handler(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainStateGroup.main, mode=StartMode.RESET_STACK)
