from typing import Tuple, Dict, Optional, Final

from discord_interactions.utils.abstracts import SingletonMeta
from .components import Component, ActionRow, Button, SelectOption, SelectMenu

# component class names
ACTION_ROW: Final[str] = ActionRow.__name__
BUTTON: Final[str] = Button.__name__
SELECT_OPTION: Final[str] = SelectOption.__name__
SELECT: Final[str] = SelectMenu.__name__


class ComponentCache(metaclass=SingletonMeta):
    __slots__ = (
        'cache'
    )

    cache: Dict[str, Dict[str, Component]]

    def __init__(self):
        self.cache: Dict[str, Dict[str, Component]] = {}

    def register_button(self, custom_id: str, button: Component) -> None:
        self.cache[BUTTON][custom_id] = button

    def get_buttons(self) -> Tuple[Component, ...]:
        return tuple(self.cache[BUTTON].values())

    def get_button_by_id(self, custom_id: str) -> Optional[Component]:
        return next(filter(
            lambda c: c.custom_id == custom_id,
            filter(lambda c: 'custom_id' in c.__dict__ and c.custom_id == custom_id, self.cache[BUTTON])
        ), None)

    def register_select_menu(self, custom_id: str, select: SelectMenu) -> None:
        self.cache[SELECT][custom_id] = select

    def get_select_menus(self) -> Tuple[Component, ...]:
        return tuple(self.cache[SELECT].values())

    def get_select_menu_by_id(self, custom_id: str) -> Optional[Component]:
        return next(filter(
            lambda c: c.custom_id == custom_id,
            filter(lambda c: 'custom_id' in c.__dict__ and c.custom_id == custom_id, self.cache[SELECT])
        ), None)
