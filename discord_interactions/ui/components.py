from __future__ import annotations

from enum import Enum
from typing import List, Optional, Final, Union

from discord import PartialEmoji

from discord_interactions.utils.type_hints import JSON, EMOJI
from discord_interactions.utils.log import get_stream_logger

# Constant Values - key
TYPE: Final[str] = 'type'
COMPONENTS: Final[str] = 'components'

__all__ = (
    'ComponentType',
    'Component',
    'ActionRow',
    'ButtonStyle',
    'Button',
    'SelectOption',
    'SelectMenu'
)

logger = get_stream_logger('discord_interactions.ui')


"""
Component base class
"""


class ComponentType(Enum):
    ActionRow = 1   # properties > type: int, components: Array<Component>
    # EMOJI = {
    #   "id": "emoji id (for custom emojis only",
    #   "name": "emoji name or unicode emoji",
    #   "animated": true
    # }
    Button = 2      # properties > label: string, style: int, custom_id: Optional<string>, url: Optional<string>, emoji: Emoji
    SelectMenu = 3    # properties > options: Array<DropdownOption>, custom_id: string,
    Select = SelectMenu

    @classmethod
    def parse(cls, value: int) -> Optional[ComponentType]:
        return next(
            filter(lambda m: m.value == value, cls.__members__.values()),
            None
        )


class Component:
    type: ComponentType

    @classmethod
    def from_json(cls, data: JSON):
        return cls(data[TYPE])

    def __init__(self, type: ComponentType):
        self.type = type

    def __repr__(self) -> str:
        return 'discord.ui.components.Component(type={})'.format(self.type.value)

    def to_dict(self) -> JSON:
        data = {
            TYPE: self.type.value
        }
        return data


"""
ActionRow
"""


class ActionRow(Component):
    child_components: List[Component]

    @classmethod
    def from_json(cls, data: JSON) -> ActionRow:
        components: List[JSON] = data[COMPONENTS]
        child_type: int = components[0][TYPE]
        if components[0][TYPE] == ComponentType.Button.value:
            # Consider this ActionRow contains buttons.
            buttons: List[Button] = list(map(lambda d: Button.from_json(d), data[COMPONENTS]))
            return cls(

            )
        elif child_type == ComponentType.Select.value:
            # Consider this ActionRow contains select menus
            return cls(

            )
        else:
            return cls()

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

    def __repr__(self) -> str:
        return 'ActionRow(components={})'.format(self.child_components)

    def __str__(self) -> str:
        return 'discord.ui.ActionRow()'


"""
Button
"""


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
    emoji: Optional[EMOJI]
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
            # Required Parameters
            style: ButtonStyle,
            # Optional Parameters
            label: Optional[str] = None,
            emoji: Optional[EMOJI] = None,
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
            data[ButtonKeys.EMOJI] = self.emoji if isinstance(self.emoji, str) else self.emoji.to_dict()
        if self.disabled is not None:
            data[ButtonKeys.DISABLED] = self.disabled
        if self.custom_id:
            data[ButtonKeys.CUSTOM_ID] = self.custom_id
        if self.url:
            data[ButtonKeys.URL] = self.url

        return data

    def __repr__(self) -> str:
        params = ['style={}'.format(self.style.value)]
        if self.label:
            params.append('label={}'.format(self.label))
        if self.emoji:
            params.append('emoji={}'.format(self.emoji if isinstance(self.emoji, str) else self.emoji.id))
        if self.disabled:
            params.append('disabled={}'.format(self.disabled))
        if self.custom_id:
            params.append('custom_id={}'.format(self.custom_id))
        if self.url:
            params.append('url={}'.format(self.url))

        return 'Button({})'.format(','.join(params))

    def __str__(self) -> str:
        # Since all buttons have either custom_id or url, we can use one of those attributes to indicate button.
        return 'discord.ui.Button({})'.format('url=[}'.format(self.url) if self.url else 'custom_id={}'.format(self.custom_id))


"""
SelectMenu & SelectOption
"""


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
        emoji_raw = data.get(SelectOptionKeys.EMOJI)
        emoji = emoji_raw if isinstance(emoji_raw, str) else PartialEmoji.from_dict(emoji_raw)

        return cls(
            data[SelectOptionKeys.LABEL],
            data[SelectOptionKeys.VALUE],
            emoji=emoji,
            description=data.get(SelectOptionKeys.DESCRIPTION),
            default=data.get(SelectOptionKeys.DEFAULT)
        )

    def __init__(
            self,
            # Required
            label: str,
            value: str,
            # Optional
            emoji: Optional[EMOJI] = None,
            description: Optional[str] = None,
            default: Optional[bool] = False,
    ):
        """

        """
        self.label = label
        self.value = value
        self.emoji = emoji
        self.description = description
        self.default = default

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

    def __repr__(self) -> str:
        params = ['label={}'.format(self.label), 'value={}'.format(self.value)]
        if self.emoji:
            params.append('emoji={}'.format(self.emoji if isinstance(self.emoji, str) else self.emoji.id))
        if self.description:
            params.append('description={}'.format(self.description))
        if self.default:
            params.append('default={}'.format(self.default))
        return 'SelectOption({})'.format(params)

    def __str__(self) -> str:
        return 'discord.ui.SelectOption(label={})'.format(self.label)


class SelectMenu(Component):
    options: List[SelectOption]
    custom_id: Optional[str]
    placeholder: Optional[str]
    min_values: Optional[int]
    max_values: Optional[int]

    @classmethod
    def from_json(cls, data: JSON):
        return cls(
            options=list(map(SelectOption.from_json, data[SelectKeys.OPTIONS])),
            placeholder=data.get(SelectKeys.PLACEHOLDER),
            min_values=data.get(SelectKeys.MIN_VALUES),
            max_values=data.get(SelectKeys.MAX_VALUES)
        )

    def __init__(
            self,
            options: List[SelectOption],
            custom_id: Optional[str] = None,
            placeholder: Optional[str] = None,
            min_values: Optional[int] = None,
            max_values: Optional[int] = None
    ):
        super(SelectMenu, self).__init__(ComponentType.Select)
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
        data = super(SelectMenu, self).to_dict()
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

    def __repr__(self) -> str:
        params = ['options=[{}]'.format(','.join(map(
            lambda o: o.__repr__(),
            self.options
        )))]
        if self.custom_id:
            params.append('custom_id={}'.format(self.custom_id))
        if self.placeholder:
            params.append('placeholder={}'.format(self.placeholder))
        if self.min_values:
            params.append('min_values={}'.format(self.min_values))
        if self.max_values:
            params.append('max_values={}'.format(self.max_values))
        return 'SelectMenu({})'.format(','.join(params))

    def __str__(self) -> str:
        return 'discord.ui.SelectMenu(custom_id={})'.format(self.custom_id)

