from __future__ import annotations

from typing import List, Optional, Union, Final

from discord import PartialEmoji

from discord_interactions.ui import Component, ComponentType
from discord_interactions.utils import JSON, EMOJI


class SelectOptionKeys:
    LABEL: Final[str] = 'label'
    VALUE: Final[str] = 'value'
    EMOJI: Final[str] = 'emoji'
    DESCRIPTION: Final[str] = 'description'
    DEFAULT: Final[str] = 'default'


class SelectKeys:
    OPTIONS: Final[str] = 'options'
    CUSTOM_ID: Final[str] = 'custom_id'
    PLACEHOLDER: Final[str] = 'placeholder'
    MIN_VALUES: Final[str] = 'min_values'
    MAX_VALUES: Final[str] = 'max_values'


class SelectOption:
    label: str
    value: str
    emoji: Optional[EMOJI]
    description: Optional[bool]
    default: Optional[bool]

    @classmethod
    def from_json(cls, data: JSON) -> SelectOption:
        return cls()

    def __init__(
            self,
            label: str,
            value: str,
            emoji: Optional[EMOJI] = None,
            description: Optional[str] = None,
            default: Optional[bool] = False,
    ):
        """

        """

    def to_json(self) -> JSON:
        data = {
            SelectOptionKeys.LABEL: self.label,
            SelectOptionKeys.VALUE: self.value
        }
        if self.emoji:
            data[SelectOptionKeys.EMOJI] = self.emoji.to_dict()
        if self.description:
            data[SelectOptionKeys.DESCRIPTION] = self.description
        if self.default:
            data[SelectOptionKeys.DEFAULT] = self.default
        return data


class Select(Component):
    options: List[SelectOption]
    custom_id: Optional[str]
    placeholder: Optional[str]
    min_values: Optional[int]
    max_values: Optional[int]

    def __init__(
            self,
            options: List[SelectOption],
            custom_id: Optional[str] = None,
            placeholder: Optional[str] = None,
            min_values: Optional[int] = None,
            max_values: Optional[int] = None
    ):
        super(Select, self).__init__(ComponentType.Select)
        self.options = options
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values

    def add_option(self, option: Union[SelectOption, dict]):
        if isinstance(option, SelectOption):
            self.options.append(option)
        elif isinstance(option, dict):
            self.options.append(SelectOption.from_json(option))
        else:
            raise TypeError('discord_interactions.ui.Select receives either SelectOption object or dictionary as an option to append.')

    def to_dict(self) -> JSON:
        data = super(Select, self).to_dict()
        data[SelectKeys.OPTIONS] = list(map(lambda o: o.to_dict(), self.options))
        if self.custom_id:
            data[SelectKeys.CUSTOM_ID] = self.custom_id
        if self.placeholder:
            data[SelectKeys.PLACEHOLDER] = self.placeholder
        if self.min_values:
            data[SelectKeys.MIN_VALUES] = self.min_values
        if self.max_values:
            data[SelectKeys.MAX_VALUES] = self.max_values

        return data
