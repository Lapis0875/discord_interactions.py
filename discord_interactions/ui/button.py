from __future__ import annotations
from enum import Enum
from typing import Union, Optional, Final

from discord import PartialEmoji, Emoji

from discord_interactions.utils import get_stream_logger, JSON
from discord_interactions.ui.components import Component, ComponentType

logger = get_stream_logger('discord_interactions.ui')


class ButtonKeys:
    # Constant Values - key
    STYLE: Final[str] = 'style'
    LABEL: Final[str] = 'label'
    EMOJI: Final[str] = 'emoji'
    DISABLED: Final[str] = 'disabled'
    CUSTOM_ID: Final[str] = 'custom_id'
    URL: Final[str] = 'url'


class ButtonStyle(Enum):
    Primary = 1
    Secondary = 2
    Success = 3
    Danger = 4
    Link = 5

    # Aliases
    Blurple = Primary
    Gray = Grey = Secondary
    Green = Success
    Red = Danger
    URL = Link

    @classmethod
    def parse(cls, value: Union[int, str]) -> Optional[ButtonStyle]:
        logger.debug('ButtonStyle(Enum) : Try parsing value {} into ButtonStyle enumeration object.'.format(value))
        return next(filter(
            lambda m: m.value == value or m.name == value,
            cls.__members__.values()
        ), None)


class Button(Component):
    style: ButtonStyle
    label: Optional[str]
    custom_id: Optional[str]
    url: Optional[str]
    emoji: Optional[Emoji]
    disabled: Optional[bool]

    @classmethod
    def from_json(cls, data: JSON) -> Button:
        return cls(
            # Required Parameters
            style=ButtonStyle.parse(data[ButtonKeys.STYLE]),
            # Optional Parameters
            label=data.get(ButtonKeys.LABEL),
            emoji=data.get(ButtonKeys.EMOJI),
            disabled=data.get(ButtonKeys.DISABLED),
            # custom_id and url cannot be used in both.
            custom_id=data.get(ButtonKeys.CUSTOM_ID),
            url=data.get(ButtonKeys.URL)
        )

    def __init__(
            self,
            style: ButtonStyle,
            label: Optional[str] = None,
            emoji: Optional[PartialEmoji] = None,
            disabled: Optional[bool] = None,
            custom_id: Optional[str] = None,
            url: Optional[str] = None
    ):
        super(Button, self).__init__(ComponentType.Button)
        self.style = style
        self.label = label
        self.emoji = emoji
        self.disabled = disabled

        # components cannot be used with style 5.
        self.custom_id = custom_id
        if custom_id and style == ButtonStyle.Link:
            raise ValueError('discord_interactions.ui.Button cannot have custom_id attribute with style 5 (ButtonStyle.Link)')
        # url must be used with style 5 (ButtonStyle.Link)
        self.url = url
        if url and style != ButtonStyle.Link:
            raise ValueError('discord_interactions.ui.Button with url attribute must have style 5 (ButtonStyle.Link)')

        # With upper checks, this button is now ensured to have either one of url or custom_id.
        # custom_id 혹은 url 속성중 하나만 가지도록 검사함.

    def to_dict(self) -> JSON:
        data = super(Button, self).to_dict()
        data[ButtonKeys.STYLE] = self.style.value
        if self.label:
            data[ButtonKeys.LABEL] = self.label
        if self.emoji:
            data[ButtonKeys.EMOJI] = self.emoji.to_dict()
        if self.disabled is not None:
            data[ButtonKeys.DISABLED] = self.disabled
        if self.url:
            data[ButtonKeys.URL] = self.url
        if self.custom_id:
            data[ButtonKeys.CUSTOM_ID] = self.custom_id

        return data
