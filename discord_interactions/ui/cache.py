from typing import Tuple, Dict, Optional

from discord_interactions.ui import Component
from discord_interactions.utils.abstracts import SingletonMeta


class ComponentCache(metaclass=SingletonMeta):
    __slots__ = (
        'cache'
    )

    cache: Dict[str, Dict[str, Component]]

    def __init__(self):
        self.cache: Dict[str, Dict[str, Component]] = {}

    def get_component_by_id(self, custom_id: str) -> Optional[Component]:
        # MOCK LOGIC
        for components in self.cache:
            for component in components:
                if 'custom_id' in component.__dict__ and component.custom_id == custom_id:
                    return component
        filter(
            lambda c: c.custom_id == custom_id,
            filter(lambda c: c)
        )

    def get_buttons(self) -> Tuple[Component, ...]:
        return tuple(self.cache['button'].values())

    def register_button(self, custom_id: str, button: Component) -> None:
        self.cache[custom_id] = button