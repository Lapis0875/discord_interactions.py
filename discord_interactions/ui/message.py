from __future__ import annotations
from typing import List, Any, Union, Optional

from discord import Message, User, Member

from discord_interactions.utils.type_hints import JSON
from .components import ComponentType, Component, ActionRow, Button, SelectMenu, SelectOption

__all__ = (
    'ComponentMessage',
    'parse_component',
    'parse_buttons'
)


def get_data_from_msg(msg: Message) -> JSON:
    data: JSON = {
        'type': msg.type,
        'id': msg.id,
        'channel_id': msg.channel.id,
        'author': get_data_from_user(msg.author),
        'attachments': msg.attachments,
        'timestamp': msg.created_at,
        'pinned': msg.pinned,
        'tts': msg.tts,
        'edited_timestamp': msg.edited_at,
        'flags': msg.flags,
        'mentions': [role.id for role in msg.mentions],
        'mention_roles': [role.id for role in msg.role_mentions],
        'mention_everyone': msg.mention_everyone,
        'content': msg.content,
        'embeds': msg.embeds
    }
    return data


def parse_component(components: List[JSON]) -> List[Any]:
    objects: List[Any] = []
    for component in components:
        if component['type'] == ComponentType.Container:
            objects.extend(parse_component(component['components']))
        elif component['type'] == ComponentType.Button:
            objects.append(Button.from_json(component))

    return objects


def parse_buttons(components: List[JSON]) -> Union[List[List[Button]], List[Button]]:
    buttons: List[Union[List[Button],Button]] = []
    for component in components:
        if component['type'] == ComponentType.Container:
            buttons.append(parse_buttons(component['components']))
        elif component['type'] == ComponentType.Button:
            buttons.append(Button.from_json(component))

    return buttons


class ComponentMessage(Message):
    @classmethod
    def fromMessage(cls, msg: Message, data: Optional[JSON] = None) -> ComponentMessage:
        return cls(
            state=msg._state,
            channel=msg.channel,
            data=get_data_from_msg(msg)
        )

    def __init__(self, *, components: List[Component] = None, **kwargs):
        super(ComponentMessage, self).__init__(**kwargs)
        self._components: List[Union[ActionRow, Button, SelectMenu]] = components or []

    @property
    def components(self) -> List[Component]:
        return self._components

    @property
    def buttons(self) -> List[Button]:
        return list(filter(lambda c: c.type == ComponentType.Button, self._components))

    @property
    def select_menus(self) -> List[SelectMenu]:
        return list(filter(lambda c: c.type == ComponentType.SelectMenu, self._components))

    def get_component(self, custom_id: str) -> Optional[Button]:
        return next(filter(
            lambda c: c.custom_id == custom_id,
            self._components
        ), None)    # Return None if no elements are found.




