from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Type

from discord import User, Role
from discord.abc import GuildChannel

from discord_interactions.application_commands.models import ApplicationCommandOptionType, ApplicationCommandOptionChoice, ApplicationCommandOption
from discord_interactions.utils.abstracts import JsonObject
from discord_interactions.utils.type_hints import JSON


__all__ = (
    'StringCommandOption',
    'IntegerCommandOption',
    'BooleanCommandOption',
    'UserCommandOption',
    'ChannelCommandOption',
    'RoleCommandOption'
)


class AnnotationObject(ABC):
    """Abstract Base Class for annotation objects"""
    @property
    @abstractmethod
    def name(self) -> str:  ...

    @abstractmethod
    def __repr__(self) -> str:  ...

    def __str__(self) -> str:
        return self.__str__()

@DeprecationWarning
class __ApplicationCommandOptionAnnotation(AnnotationObject, JsonObject):
    @classmethod
    def fromJson(cls, data: JSON) -> __ApplicationCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            option_type=ApplicationCommandOptionType.parse(data['type']),
            default=data.get('default'),
            required=data.get('required'),
            choices=data.get('choices'),
            options=data.get('options')
        )

    def __init__(
        self,
        name: str,
        description: str,
        option_type: ApplicationCommandOptionType,
        default: Optional[bool] = None,
        required: Optional[bool] = None,
        choices: Optional[List[ApplicationCommandOptionChoice]] = None,
        options: Optional[List[ApplicationCommandOption]] = None
    ):
        self._name: str = name
        self._description: str = description
        self._type: ApplicationCommandOptionType = option_type
        self._default: Optional[bool] = default
        self._required: Optional[bool] = required

        if choices is not None:
            if option_type != ApplicationCommandOptionType.INTEGER and option_type != ApplicationCommandOptionType.STRING:
                raise ValueError("parameter 'choices' can only be used with ApplicationCommandOptionType.INTEGER and ApplicationCommandOptionType.STRING")
            self._choices: List[ApplicationCommandOptionChoice] = choices
        if options is not None:
            if option_type != ApplicationCommandOptionType.SUB_COMMAND and option_type != ApplicationCommandOptionType.SUB_COMMAND_GROUP:
                raise ValueError("parameter 'options' can only be used with ApplicationCommandOptionType.SUB_COMMAND and ApplicationCommandOptionType.SUB_COMMAND_GROUP")
            self._options: List[ApplicationCommandOption] = options

        # Value storage for command invoke
        self._value: Any = None

    def getParameter(self) -> Dict[str, Any]:
        return {self.name: self._value}

    def toCommandOption(self) -> ApplicationCommandOption:
        return ApplicationCommandOption(
            name=self._name,
            description=self._description,
            option_type=self._type,
            required=self._required,
            default=self._default,
            choices=self._choices,
            options=self._options
        )

    def toJson(self) -> JSON:
        return self.toCommandOption().toJson()

    def setOptionValue(self, value: Any):
        self._value = value

    def __repr__(self):
        return 'ApplicationCommandOptionAnnotation(name={})'.format(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def type(self) -> ApplicationCommandOptionType:
        return self._type

    option_type = type  # Alias

    @property
    def required(self) -> Optional[bool]:
        return getattr(self, '_required', None)

    @property
    def default(self) -> Optional[bool]:
        return getattr(self, '_default', None)

    @property
    def choices(self) -> Optional[List[ApplicationCommandOptionChoice]]:
        return getattr(self, '_choices', None)

    @property
    def options(self) -> Optional[List[ApplicationCommandOptionChoice]]:
        return getattr(self, '_options', None)


class ApplicationCommandOptionAnnotation(AnnotationObject, JsonObject):
    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            option_type=ApplicationCommandOptionType.parse(data['type']),
            default=data.get('default'),
            required=data.get('required')
        )

    def __init__(
        self,
        name: str,
        description: str,
        option_type: ApplicationCommandOptionType,
        default: Optional[bool] = None,
        required: Optional[bool] = None
    ):
        self._name: str = name
        self._description: str = description
        self._type: ApplicationCommandOptionType = option_type
        self._required: Optional[bool] = required
        self._default: Optional[bool] = default

        # Value storage for command invoke
        self._value: Any = None

    def getParameter(self) -> Dict[str, Any]:
        return {self.name: self._value}

    def toCommandOption(self) -> ApplicationCommandOption:
        return ApplicationCommandOption(
            name=self._name,
            description=self._description,
            option_type=self._type,
            required=self._required,
            default=self._default
        )

    def toJson(self) -> JSON:
        return self.toCommandOption().toJson()

    def setOptionValue(self, value: Any):
        self._value = value

    def __repr__(self):
        return 'ApplicationCommandOptionAnnotation(name={})'.format(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def type(self) -> ApplicationCommandOptionType:
        return self._type

    option_type = type  # Alias

    @property
    def required(self) -> bool:
        return self._required

    @property
    def default(self) -> bool:
        return self._default


class CommandOptionWithChoices(ApplicationCommandOptionAnnotation):
    @classmethod
    def fromJson(cls, data: JSON) -> CommandOptionWithChoices:
        return cls(
            name=data['name'],
            description=data['description'],
            option_type=data['type'],
            required=data.get('required'),
            default=data.get('default'),
            choices=data.get('choices')
        )

    @property
    def choices(self) -> Optional[List[ApplicationCommandOptionChoice]]:
        return self._choices

    def __init__(
        self,
        name: str,
        description: str,
        option_type: ApplicationCommandOptionType,
        required: Optional[bool] = None,
        default: Optional[bool] = None,
        choices: Optional[List[ApplicationCommandOptionChoice]] = None
    ):
        super(CommandOptionWithChoices, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.INTEGER,
            required=required,
            default=default
        )

        self._choices: Optional[List[ApplicationCommandOptionChoice]] = choices

    def toCommandOption(self) -> ApplicationCommandOption:
        return ApplicationCommandOption(
            name=self._name,
            description=self._description,
            option_type=self._type,
            required=self.required,
            default=self.default
        )

    def __repr__(self):
        return 'ApplicationCommandOptionAnnotation.withChoices(name={})'.format(self._name)


class CommandOptionWithOptions(ApplicationCommandOptionAnnotation):
    @classmethod
    def fromJson(cls, data: JSON) -> CommandOptionWithOptions:
        return cls(
            name=data['name'],
            description=data['description'],
            option_type=data['type'],
            required=data.get('required'),
            default=data.get('default'),
            options=data.get('choices')
        )

    @property
    def options(self) -> Optional[List[ApplicationCommandOption]]:
        return self._options

    def __init__(
        self,
        name: str,
        description: str,
        option_type: ApplicationCommandOptionType,
        required: Optional[bool] = None,
        default: Optional[bool] = None,
        options: Optional[List[ApplicationCommandOption]] = None
    ):
        super(CommandOptionWithOptions, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.INTEGER,
            required=required,
            default=default
        )

        self._options: Optional[List[ApplicationCommandOptionChoice]] = options

    def toCommandOption(self) -> ApplicationCommandOption:
        return ApplicationCommandOption(
            name=self._name,
            description=self._description,
            option_type=self._type,
            required=self.required,
            default=self.default
        )

    def __repr__(self):
        return 'ApplicationCommandOptionAnnotation.withOptions(name={})'.format(self._name)


class StringCommandOptionAnnotation(CommandOptionWithChoices):
    @classmethod
    def fromJson(cls, data: JSON) -> StringCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            required=data.get('required'),
            default=data.get('default'),
            choices=data.get('choices')
        )

    def __init__(
        self,
        name: str,
        description: str,
        required: Optional[bool] = None,
        default: Optional[bool] = None,
        choices: Optional[List[ApplicationCommandOptionChoice]] = None
    ) -> None:   # For type hint utilities
        super(StringCommandOptionAnnotation, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.STRING,
            required=required,
            default=default,
            choices=choices
        )

    def __repr__(self):
        return 'StringCommandOptionAnnotation(name={})'.format(self._name)


def StringCommandOption(
        name: str,
        description: str,
        required: bool = False,
        default: bool = False,
        choices: Optional[List[ApplicationCommandOptionChoice]] = None
) -> Type[str]:
    """
    Builder function of StringCommandOptionAnnotation.
    We need to use function to create command option annotations, due to provide normal type hint functionality.

    Args:
        name (str): name of the command option
        description (str): description of the command option
        required (bool): flag value of command option requirement. 'False' in default.
        default (bool): flag value which indicates whether to set this option as default or not.
        choices (Optional[List[ApplicationCommandOptionChoice]]): command option choices.
    """
    return StringCommandOptionAnnotation(name, description, required, default)


class IntegerCommandOptionAnnotation(CommandOptionWithChoices):
    @classmethod
    def fromJson(cls, data: JSON) -> IntegerCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            required=data.get('required'),
            default=data.get('default'),
            choices=data.get('choices')
        )

    def __init__(
        self,
        name: str,
        description: str,
        required: Optional[bool] = None,
        default: Optional[bool] = None,
        choices: Optional[List[ApplicationCommandOptionChoice]] = None
    ):
        super(IntegerCommandOptionAnnotation, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.INTEGER,
            required=required,
            default=default,
            choices=choices
        )

    def __repr__(self):
        return 'IntegerCommandOptionAnnotation(name={})'.format(self._name)


def IntegerCommandOption(
        name: str,
        description: str,
        required: bool = False,
        default: bool = False,
        choices: Optional[List[ApplicationCommandOptionChoice]] = None
) -> Type[int]:
    """
    Builder function of IntegerCommandOptionAnnotation.
    We need to use function to create command option annotations, due to provide normal type hint functionality.

    Args:
        name (str): name of the command option
        description (str): description of the command option
        required (bool): flag value of command option requirement. 'False' in default.
        default (bool): flag value which indicates whether to set this option as default or not.
        choices (Optional[List[ApplicationCommandOptionChoice]]): command option choices.
    """
    return IntegerCommandOptionAnnotation(name, description, required, default, choices)


class BooleanCommandOptionAnnotation(ApplicationCommandOptionAnnotation):
    @classmethod
    def fromJson(cls, data: JSON) -> BooleanCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            required=data.get('required'),
            default=data.get('default')
        )

    def __init__(
        self,
        name: str,
        description: str,
        required: Optional[bool] = None,
        default: Optional[bool] = None
    ):
        super(BooleanCommandOptionAnnotation, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.BOOLEAN,
            required=required,
            default=default
        )

    def __repr__(self) -> str:
        return 'BooleanCommandOptionAnnotation(name={})'.format(self._name)


def BooleanCommandOption(
        name: str,
        description: str,
        required: bool = False,
        default: bool = False
) -> Type[bool]:
    """
    Builder function of BooleanCommandOptionAnnotation.
    We need to use function to create command option annotations, due to provide normal type hint functionality.

    Args:
        name (str): name of the command option
        description (str): description of the command option
        required (bool): flag value of command option requirement. 'False' in default.
        default (bool): flag value which indicates whether to set this option as default or not.
    """
    return BooleanCommandOptionAnnotation(name, description, required, default)


class UserCommandOptionAnnotation(ApplicationCommandOptionAnnotation):
    @classmethod
    def fromJson(cls, data: JSON) -> UserCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            required=data.get('required'),
            default=data.get('default')
        )

    def __init__(
        self,
        name: str,
        description: str,
        required: Optional[bool] = None,
        default: Optional[bool] = None
    ):
        super(UserCommandOptionAnnotation, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.BOOLEAN,
            required=required,
            default=default
        )

    def __repr__(self) -> str:
        return 'UserCommandOptionAnnotation(name={})'.format(self._name)


def UserCommandOption(name: str, description: str, required: bool = False, default: bool = False) -> Type[User]:
    """
    Builder function of UserCommandOptionAnnotation.
    We need to use function to create command option annotations, due to provide normal type hint functionality.

    Args:
        name (str): name of the command option
        description (str): description of the command option
        required (bool): flag value of command option requirement. 'False' in default.
        default (bool): flag value which indicates whether to set this option as default or not.
    """
    return UserCommandOptionAnnotation(name, description, required, default)


class ChannelCommandOptionAnnotation(ApplicationCommandOptionAnnotation):
    @classmethod
    def fromJson(cls, data: JSON) -> ChannelCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            required=data.get('required'),
            default=data.get('default')
        )

    def __init__(
        self,
        name: str,
        description: str,
        required: Optional[bool] = None,
        default: Optional[bool] = None
    ):
        super(ChannelCommandOptionAnnotation, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.BOOLEAN,
            required=required,
            default=default
        )

    def __repr__(self) -> str:
        return 'ChannelCommandOptionAnnotation(name={})'.format(self._name)


def ChannelCommandOption(name: str, description: str, required: bool = False, default: bool = False) -> Type[GuildChannel]:
    """
    Builder function of UserCommandOptionAnnotation.
    We need to use function to create command option annotations, due to provide normal type hint functionality.

    Args:
        name (str): name of the command option
        description (str): description of the command option
        required (bool): flag value of command option requirement. 'False' in default.
        default (bool): flag value which indicates whether to set this option as default or not.
    """
    return ChannelCommandOptionAnnotation(name, description, required, default)


class RoleCommandOptionAnnotation(ApplicationCommandOptionAnnotation):
    @classmethod
    def fromJson(cls, data: JSON) -> RoleCommandOptionAnnotation:
        return cls(
            name=data['name'],
            description=data['description'],
            required=data.get('required'),
            default=data.get('default')
        )

    def __init__(
        self,
        name: str,
        description: str,
        required: Optional[bool] = None,
        default: Optional[bool] = None
    ):
        super(RoleCommandOptionAnnotation, self).__init__(
            name=name,
            description=description,
            option_type=ApplicationCommandOptionType.BOOLEAN,
            required=required,
            default=default
        )

    def __repr__(self) -> str:
        return 'RoleCommandOptionAnnotation(name={})'.format(self._name)


def RoleCommandOption(name: str, description: str, required: bool = False, default: bool = False) -> Type[Role]:
    """
    Builder function of UserCommandOptionAnnotation.
    We need to use function to create command option annotations, due to provide normal type hint functionality.

    Args:
        name (str): name of the command option
        description (str): description of the command option
        required (bool): flag value of command option requirement. 'False' in default.
        default (bool): flag value which indicates whether to set this option as default or not.
    """
    return RoleCommandOptionAnnotation(name, description, required, default)


