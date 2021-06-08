from __future__ import annotations

from enum import Enum
from typing import List, Optional, Final

from discord_interactions.utils.type_hints import JSON

# Constant Values - key
TYPE: Final[str] = 'type'
COMPONENTS: Final[str] = 'components'


class ComponentType(Enum):
    ActionRow = 1   # properties > type: int, components: Array<Component>
    # EMOJI = {
    #   "id": "emoji id (for custom emojis only",
    #   "name": "emoji name or unicode emoji",
    #   "animated": true
    # }
    Button = 2      # properties > label: string, style: int, custom_id: Optional<string>, url: Optional<string>, emoji: Emoji
    Select = 3    # properties > options: Array<DropdownOption>, custom_id: string,

    @classmethod
    def parse(cls, value: int) -> Optional[ComponentType]:
        return next(
            filter(lambda m: m.value == value, cls.__members__.values()),
            None
        )


class Component:
    type: ComponentType

    def __init__(self, type: ComponentType):
        self.type = type

    def __repr__(self) -> str:
        return 'discord.ui.components.Component(type={})'.format(self.type.value)

    def to_dict(self) -> JSON:
        data = {
            TYPE: self.type.value
        }
        return data


class ActionRow(Component):
    child_components: List[Component]

    @classmethod
    def from_json(cls, data: JSON) -> ActionRow:
        components: List[JSON] = data[COMPONENTS]
        if components[0][TYPE] == ComponentType.Button.value:
            # Consider this ActionRow contains buttons.
            return cls(

            )
        return cls(
        )

    def __init__(self, child_components: List[Component] = None):
        super(ActionRow, self).__init__(ComponentType.ActionRow)
        self.child_components = child_components or []

    def add_child(self, child: Component):
        if not isinstance(child, Component):
            raise TypeError('discord_interactions.ui.ActionRow can receive child components which subclass Component class.')
        self.child_components.append(child)

    def to_dict(self) -> JSON:
        data = super(ActionRow, self).to_dict()
        data.update({
                COMPONENTS: list(map(lambda c: c.to_dict(), self.child_components))
        })
        return data


