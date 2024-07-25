import inspect
import logging
from typing import Awaitable, Callable, TypedDict, TypeVar

from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input.text import ManagedTextInput, OnError, OnSuccess


USER_NAME = "__user"
IS_NEW_NAME = "__is_new"

date_reservation_time = [
    "10:00",
    "11:15",
    "12:30",
    "13:45",
    "15:00",
    "16:15",
    "17:30",
    "18:45",
    "20:00",
]


class ErrorWindowData(TypedDict):
    error: str | None
    has_error: bool


def error_getter(func) -> Callable[[...], Awaitable[ErrorWindowData]]:
    async def getter(dialog_manager: DialogManager, **_) -> ErrorWindowData:
        if "error" in dialog_manager.dialog_data:
            return ErrorWindowData(
                error=dialog_manager.dialog_data["error"],
                has_error=True,
            )
        value = await func(dialog_manager, **_)
        returning = ErrorWindowData(error=None, has_error=False)
        if value is not None:
            returning.update(**value)

        return returning

    return getter


T = TypeVar("T")

logger = logging.getLogger("Django")


def on_input_success(
    field_name: str,
    next_state: State,
    *validators: Callable[[T, DialogManager], Awaitable | None],
) -> OnSuccess:
    async def on_success(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        data: T,
    ):
        for validator in validators:
            try:
                if inspect.iscoroutinefunction(validator):
                    await validator(data, dialog_manager)
                else:
                    validator(data, dialog_manager)
            except ValueError as e:
                dialog_manager.dialog_data["error"] = str(e)
                return
        dialog_manager.dialog_data[field_name] = data
        dialog_manager.dialog_data.pop("error", None)
        logger.debug(
            "everything correct. Assigned: %s-%s, Switching to %s",
            field_name,
            data,
            next_state.state,
        )
        await dialog_manager.switch_to(next_state)

    return on_success


def on_input_error() -> OnError:
    async def on_error(
        message: Message,
        widget: ManagedTextInput[T],
        dialog_manager: DialogManager,
        error: ValueError,
    ):
        dialog_manager.dialog_data["error"] = str(error)

    return on_error
