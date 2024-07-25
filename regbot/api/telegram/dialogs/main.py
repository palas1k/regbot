import logging

from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Start, Button
from aiogram_dialog.widgets.text import Const

from regbot.api.telegram.dialogs.crud_reg import CRUDRegStateGroup, check_reg

logger = logging.getLogger(__name__)


class MainStateGroup(StatesGroup):
    main = State()


main_window = Dialog(
    Window(
        Const("Добро пожаловать в бот\n" "Здесь вы можете:\n"),
        Group(
            Button(Const("Записаться ->"), id="reg", on_click=check_reg),
            Start(
                Const("Посмотреть свою запись ->"),
                id="get",
                state=CRUDRegStateGroup.get_reg,
            ),
            Start(Const("Отменить запись"), id="del", state=CRUDRegStateGroup.get_reg),
            width=1,
        ),
        state=MainStateGroup.main,
    ),
)
