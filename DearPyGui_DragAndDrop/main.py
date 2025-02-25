from __future__ import annotations

import traceback
from enum import IntEnum
from pathlib import Path
from typing import Type, TypeVar, Dict, Callable, Any, Union, List
import win32com.shell.shellcon as shellcon

import dearpygui.dearpygui as dpg

DragAndDropDataObject = Union[None, str, List[Path]]
SubscriptionTag = TypeVar('SubscriptionTag', bound=int)


class KEYSTATE(IntEnum):
    LEFT = 1
    RIGHT = 2
    SHIFT = 4
    CTRL = 8
    MIDDLE = 16
    ALT = 32


class DROPEFFECT(IntEnum):
    NONE = 0
    COPY = 1
    MOVE = 2
    LINK = 4
    SCROLL = 0x80000000


_now_drop_effect: DROPEFFECT = DROPEFFECT.MOVE


def set_drop_effect(effect: DROPEFFECT = DROPEFFECT.NONE):
    global _now_drop_effect
    _now_drop_effect = effect


def get_drop_effect() -> DROPEFFECT:
    return _now_drop_effect


class DragAndDrop():
    __subscribers: Dict[SubscriptionTag, Type[DragAndDrop]] = {}
    __subscription_tag: SubscriptionTag = None

    def DragEnter(self, dataObject: DragAndDropDataObject, keyState: list[KEYSTATE]) -> bool:
        ...

    def DragOver(self, keyState: list[KEYSTATE]) -> bool:
        ...

    def DragLeave(self) -> bool:
        ...

    def Drop(self, dataObject: DragAndDropDataObject, keyState: list[KEYSTATE]) -> bool:
        ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__subscription_tag:
            self._unsubscribe(self.__subscription_tag)
        self.__subscription_tag = self._subscribe(self)  # noqa

    def __del__(self):
        if self.__subscription_tag:
            self._unsubscribe(self.__subscription_tag)

    @classmethod
    def _subscribe(cls, self: Type[DragAndDrop]) -> SubscriptionTag:
        subscription_tag = dpg.generate_uuid()
        cls.__subscribers[subscription_tag] = self
        return subscription_tag

    @classmethod
    def _unsubscribe(self, subscription_tag: SubscriptionTag):
        if subscription_tag in self.__subscribers:
            del self.__subscribers[subscription_tag]

    @classmethod
    def _DragEnter(cls, dataObject, keyState):
        for self in cls.__subscribers.values():
            try:
                if self.DragEnter(dataObject, keyState):  # noqa
                    return
            except Exception:
                traceback.print_exc()
        set_drop_effect(DROPEFFECT.NONE)

    @classmethod
    def _DragOver(cls, keyState):
        for self in cls.__subscribers.values():
            try:
                if self.DragOver(keyState):  # noqa
                    return
            except Exception:
                traceback.print_exc()
        set_drop_effect(DROPEFFECT.NONE)

    @classmethod
    def _DragLeave(cls):
        for self in cls.__subscribers.values():
            try:
                if self.DragLeave():  # noqa
                    return
            except Exception:
                traceback.print_exc()
        set_drop_effect(DROPEFFECT.NONE)

    @classmethod
    def _Drop(cls, dataObject, keyState):
        for self in cls.__subscribers.values():
            try:
                if self.Drop(dataObject, keyState):  # noqa
                    return
            except Exception:
                traceback.print_exc()
        set_drop_effect(DROPEFFECT.NONE)


class _DragAndDropForFunctions(DragAndDrop):
    def DragEnter(self, dataObject, keyState):
        ...

    def DragOver(self, keyState):
        ...

    def DragLeave(self):
        ...

    def Drop(self, dataObject, keyState):
        ...


def set_drag_enter(function: Callable[[DragAndDropDataObject, list[KEYSTATE]], Any] = None):
    if function is None:
        function = lambda *args, **kwargs: ...
    _DragAndDropForFunctions.DragEnter = function


def set_drag_over(function: Callable[[list[KEYSTATE]], Any] = None):
    if function is None:
        function = lambda *args, **kwargs: ...
    _DragAndDropForFunctions.DragOver = function


def set_drag_leave(function: Callable[[], Any] = None):
    if function is None:
        function = lambda *args, **kwargs: ...
    _DragAndDropForFunctions.DragLeave = function


def set_drop(function: Callable[[DragAndDropDataObject, list[KEYSTATE]], Any] = None):
    if function is None:
        function = lambda *args, **kwargs: ...
    _DragAndDropForFunctions.Drop = function
