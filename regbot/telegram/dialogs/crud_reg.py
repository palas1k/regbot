import datetime
import logging
from typing import Any, TypedDict

from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, ChatEvent, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import (
    CalendarConfig,
    ManagedCalendar,
    Button,
    Select,
    Cancel,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Const, Format, Case

from django.db.models import CharField, Value, Func, F as DjangoF

from gunicorn.http import Message

from regbot.models import ReservedTime
from regbot.telegram.utils import date_reservation_time, T, error_getter
from regbot.telegram.validators import PhoneNumberValidator
from regbot.telegram.widgets import CustomCalendar

logger = logging.getLogger(__name__)


class CRUDRegStateGroup(StatesGroup):
    check_reg = State()
    create_reg = State()
    reservation_time = State()
    get_number = State()
    final = State()
    get_reg = State()
    delete_reg = State()


class MainWindowGetterDate(TypedDict):
    times: list[ReservedTime]


async def on_reservation_date_selected(
    event: ChatEvent,
    widget: ManagedCalendar,
    dialog_manager: DialogManager,
    selected_date: datetime.date,
):
    dialog_manager.dialog_data["reservation_date"] = selected_date
    dialog_manager.dialog_data["reservation_date_str"] = selected_date.strftime(
        "%d-%m-%Y"
    )
    await dialog_manager.switch_to(CRUDRegStateGroup.reservation_time)


async def reservation_time_getter(dialog_manager: DialogManager, **_):
    reserved_time_template: list = date_reservation_time
    reserved_day = dialog_manager.dialog_data["reservation_date"]
    reserved_times = [
        reserved_time
        async for reserved_time in ReservedTime.objects.filter(
            date_time__year=reserved_day.year, date_time__day=reserved_day.day
        ).values_list("date_time")
    ]
    for hour in reserved_times:
        if reserved_time_template is None:
            return {"empty": "Все занято"}
        elif hour[0].strftime("%H:%M") in reserved_time_template:
            reserved_time_template.remove(hour[0].strftime("%H:%M"))
    dialog_manager.dialog_data["times"] = reserved_time_template
    return {"times": reserved_time_template, "count": len(reserved_time_template)}


async def on_reservation_time_selected(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    selected: str,
):
    dialog_manager.dialog_data["reservation_time_selected"] = selected
    await dialog_manager.switch_to(CRUDRegStateGroup.get_number)


async def number_handler(
    message: Message,
    widget: ManagedTextInput[T],
    dialog_manager: DialogManager,
    data: T,
):
    dialog_manager.dialog_data["number"] = data
    await dialog_manager.switch_to(CRUDRegStateGroup.final)


async def error(
    message: Message, dialog_: Any, dialog_manager: DialogManager, error_: ValueError
):
    dialog_manager.dialog_data["error"] = (
        "Вы ввели номер не правильно. Попробуйте еще раз"
    )
    return error


@error_getter
async def getter(dialog_manager: DialogManager, **_):
    pass


async def save_reg(
    query: CallbackQuery, widget: Button, dialog_manager: DialogManager, **_
):
    time = dialog_manager.dialog_data["reservation_time_selected"]
    date_time = dialog_manager.dialog_data["reservation_date"]
    await ReservedTime.objects.acreate(
        date_time=datetime.datetime.combine(
            date_time, datetime.datetime.strptime(time, "%H:%M").time()
        ),
        user=query.from_user.full_name,
        tg_id=query.from_user.id,
        phone_number=dialog_manager.dialog_data["number"],
    )
    await query.answer("Вы записались!")
    await dialog_manager.done()


async def reg_getter(dialog_manager: DialogManager, **_):
    today = datetime.date.today()
    try:
        res = [
            reserved_time
            async for reserved_time in ReservedTime.objects.filter(
                tg_id=dialog_manager.event.from_user.id, date_time__gte=today
            )
            .annotate(
                str_date=Func(
                    DjangoF("date_time"),
                    Value("DD-MM-YYYY HH24:MI"),
                    function="to_char",
                    output_field=CharField(),
                )
            )
            .values("id", "str_date")
        ]
    except ReservedTime.DoesNotExist:
        await dialog_manager.event.answer("Вы не записаны!")
        await dialog_manager.done()
    else:
        return MainWindowGetterDate(times=res)


async def time_selected(
    query: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    selected_time: str,
):
    dialog_manager.dialog_data["time_selected"] = selected_time
    await dialog_manager.switch_to(CRUDRegStateGroup.delete_reg)


async def delete_reg(
    query: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    res = await ReservedTime.objects.aget(
        pk=dialog_manager.dialog_data["time_selected"]
    )
    await res.adelete()
    await dialog_manager.event.answer("Запись отменена")
    await dialog_manager.done()


main_window = Dialog(
    Window(
        Const("Выберите дату:"),
        CustomCalendar(
            "reservation_date",
            id="reservation_date",
            config=CalendarConfig(
                min_date=datetime.date.today(),
                max_date=datetime.date.today() + datetime.timedelta(weeks=2),
            ),
            on_click=on_reservation_date_selected,
        ),
        state=CRUDRegStateGroup.create_reg,
    ),
    Window(
        Const("Выберите время:", when=F["dialog_data"]["times"]),
        Const("Все занято:(", when=~F["dialog_data"]["times"]),
        ScrollingGroup(
            Select(
                Format("{item}"),
                id="reservation_time",
                item_id_getter=lambda item: item,
                items="times",
                on_click=on_reservation_time_selected,
            ),
            width=1,
            height=10,
            id="times_list_pager",
        ),
        Cancel(Const("Назад"), id="1back"),
        state=CRUDRegStateGroup.reservation_time,
        getter=reservation_time_getter,
    ),
    Window(
        Case(
            {
                False: Format("Введите номер телефона"),
                True: Format("{error}"),
            },
            selector="has_error",
        ),
        TextInput(
            id="input_number",
            on_success=number_handler,
            on_error=error,
            type_factory=PhoneNumberValidator(),
        ),
        Cancel(Const("Назад"), id="2back"),
        state=CRUDRegStateGroup.get_number,
        getter=getter,
    ),
    Window(
        Format(
            "Вы записываетесь на {dialog_data[reservation_date_str]} {dialog_data[reservation_time_selected]}?"
        ),
        Button(Const("Да"), on_click=save_reg, id="save_reg"),
        Cancel(Const("Нет"), id="3back"),
        state=CRUDRegStateGroup.final,
    ),
    Window(
        Const("Ваши записи\n" "Если хотите отменить, нажмите на запись"),
        ScrollingGroup(
            Select(
                Format("{item[str_date]}"),
                id="reserved_times",
                item_id_getter=lambda item: item["id"],
                items="times",
                on_click=time_selected,
            ),
            width=1,
            height=10,
            id="times_list_pager",
        ),
        Cancel(Const("Назад"), id="4back"),
        getter=reg_getter,
        state=CRUDRegStateGroup.get_reg,
    ),
    Window(
        Const("Вы уверены что хотите отменить запись?"),
        Button(Const("Да"), on_click=delete_reg, id="delete_reg"),
        Cancel(Const("Нет"), id="5back"),
        state=CRUDRegStateGroup.delete_reg,
    ),
)
