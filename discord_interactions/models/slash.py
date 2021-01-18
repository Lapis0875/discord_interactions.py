from __future__ import annotations

import asyncio
import collections
from abc import ABCMeta, abstractmethod
from enum import IntFlag, Enum
from typing import Union, Optional, List, Callable, Coroutine, Any, NoReturn, Dict, Tuple

import aiohttp
from discord.ext.commands import Bot

from .discordAPI import DiscordAPI
from discord_interactions.utils.type_hints import JSON, CoroutineFunction
from discord_interactions.utils.abstracts import JsonObject


class InteractionType(Enum):
    PING = 1
    APPLICATION_COMMAND = 2


class InteractionResponseType(Enum):
    PONG = 1
    ACKNOWLEDGE = 2
    CHANNEL_MESSAGE = 3
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    ACKNOWLEDGE_WITH_SOURCE = 5


class InteractionResponseFlags(IntFlag):
    """Interaction Response Flags."""
    # this message has been published to subscribed channels (via Channel Following)
    CROSSPOSTED = 1 << 0

    # this message originated from a message in another channel (via Channel Following)
    IS_CROSSPOST = 1 << 1

    # do not include any embeds when serializing this message
    SUPPRESS_EMBEDS = 1 << 2

    # the source message for this crosspost has been deleted (via Channel Following)
    SOURCE_MESSAGE_DELETED = 1 << 3

    # this message came from the urgent message system
    URGENT = 1 << 4

    # Only author can see message. Hidden to others. Example : Clyde's message
    EPHEMERAL = 1 << 6


class ApplicationCommandOptionChoice(JsonObject):

    def __init__(self, name: str, value: Union[str, int]) -> None:
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Union[str, int]:
        return self._value

    @classmethod
    def fromJson(cls, data: JSON) -> SlashCommandOptionChoice:
        return cls(name=data['name'], value=data['value'])

    def toJson(self) -> JSON:
        return {
            'name': self._name,
            'value': self._value
        }


SlashCommandOptionChoice = ApplicationCommandOptionChoice  # Alias


class ApplicationCommandOptionType(Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8

    @classmethod
    def parseType(cls, value) -> ApplicationCommandOptionType:
        print(cls.__members__.values())
        return tuple(filter(lambda m: m.value == value, cls.__members__.values()))[0]


SlashCommandOptionType = ApplicationCommandOptionType  # Alias


class ApplicationCommandOption(JsonObject):
    """
    # structure
    type	    int	                                    value of ApplicationCommandOptionType
    name	    string	                                1-32 character name
    description	string	                                1-100 character description
    default?	bool	                                the first required option for the user to complete--only one option can be default
    required?	bool	                                if the parameter is required or optional--default false
    choices?	array of ApplicationCommandOptionChoice	choices for string and int types for the user to pick from
    options?	array of ApplicationCommandOption	    if the option is a subcommand or subcommand group type, this nested options will be the parameters

    # sample command option object
    {
        "name": "animal",
        "description": "The type of animal",
        "type": 3,
        "required": True,
        "choices": [
            {
                "name": "Dog",
                "value": "animal_dog"
            },
            {
                "name": "Cat",
                "value": "animal_dog"
            },
            {
                "name": "Penguin",
                "value": "animal_penguin"
            }
        ]
    }
    """

    def __init__(self, data: JSON) -> None:
        self._data = data
        self._name: str = data['name']
        self._description: str = data['description']
        self._type: ApplicationCommandOptionType = ApplicationCommandOptionType.parseType(data['type'])
        self._default = data['default'] if data.get('default') is not None else False
        self._required = data['required'] if data.get('required') is not None else False

        # parse choices
        choices = data.get('choices')
        if choices is not None:
            if self._type != ApplicationCommandOptionType.STRING or self._type != ApplicationCommandOptionType.INTEGER:
                raise ValueError('Only commands with String and Integer CommandOptionType can have choices.')
            choiceObjects = []
            for choiceJson in choices:
                choiceObjects.append(ApplicationCommandOptionChoice.fromJson(choiceJson))

            self.choices = tuple(choiceObjects)

        # parse options
        options = data.get('options')
        if options is not None:
            if self._type != ApplicationCommandOptionType.SUB_COMMAND or self._type != ApplicationCommandOptionType.SUB_COMMAND_GROUP:
                raise ValueError(
                    'Only commands with SUB_COMMAND and SUB_COMMAND_GROUP CommandOptionType can have options.')
            optionObjects = []
            for choiceJson in choices:
                optionObjects.append(ApplicationCommandOptionChoice.fromJson(choiceJson))

            self.options = tuple(optionObjects)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def type(self) -> ApplicationCommandOptionType:
        return self._type

    @property
    def default(self) -> bool:
        return self._default

    @property
    def required(self) -> bool:
        return self._required

    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommandOption:
        return cls(data)

    def toJson(self) -> JSON:
        return self._data


SlashCommandOption = ApplicationCommandOption  # Alias


class ApplicationSubCommandGroup(ApplicationCommandOption):
    """
    SubCommandGroup of Slash Command
    """

    def __init__(self, data: JSON) -> None:
        data.update(type=ApplicationCommandOptionType.SUB_COMMAND_GROUP.value)
        super().__init__(data.update())
        self.subcommands: List[ApplicationSubCommand] = []

    def subCommand(self, data: JSON) -> ApplicationSubCommand:
        return ApplicationSubCommand(data, subcommandGroup=self)

    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommandOption:
        pass

    def toJson(self) -> JSON:
        return self._data


SlashSubCommandGroup = ApplicationSubCommandGroup  # Alias


class ApplicationSubCommand(ApplicationCommandOption):
    """
    SubCommand of Slash Command
    """

    def __init__(
            self,
            data: JSON,
            subcommandGroup: Optional[ApplicationSubCommandGroup] = None
    ) -> NoReturn:
        data.update(type=ApplicationCommandOptionType.SUB_COMMAND.value)
        super().__init__(data)


SlashSubCommand = ApplicationSubCommand  # Alias


class ApplicationCommand(JsonObject):
    """
    V5 Application Command(a.k.a Slash Command) object.

    # structure : https://github.com/discord/discord-api-docs/blob/feature/interactions/docs/interactions/Slash_Commands.md#applicationcommand
    id	            snowflake	                        unique id of the command
    application_id	snowflake	                        unique id of the parent application
    name	        string	                            3-32 character name
    description	    string	                            1-100 character description
    options?	    array of ApplicationCommandOption	the parameters for the command

    # sample command creation payload
    {
        "name": "blep",
        "description": "Send a random adorable animal photo",
        "options": [
            {
                "name": "animal",
                "description": "The type of animal",
                "type": 3,
                "required": True,
                "choices": [
                    {
                        "name": "Dog",
                        "value": "animal_dog"
                    },
                    {
                        "name": "Cat",
                        "value": "animal_dog"
                    },
                    {
                        "name": "Penguin",
                        "value": "animal_penguin"
                    }
                ]
            },
            {
                "name": "only_smol",
                "description": "Whether to show only baby animals",
                "type": 5,
                "required": False
            }
        ]
    }
    """

    def __init__(
            self,
            name: str,
            description: Optional[str] = None,
            id: Optional[int] = None,
            applicationId: Optional[int] = None,
            options: Optional[List[JSON]] = None,
            callback: Optional[CoroutineFunction] = None    # Make callback functions can be set later (when fetching exising slash commands from api)
    ):
        """Initialize Slash Command object. Must be called in SlashCommand.create()
        Args:
            applicationId (int): id of V5 Application where this Slash Command is registered.
            data (JSON): JSON value of the Slash Command.
                {
                    'id': <int: id of ApplicationCommand>,
                    'application_id': <int: id of discord application where this command is registered>
                    'name': <str: name of the command>,
                    'description': <str: description of the command>,
                    'options': <>
                }
            coro (CoroutineFunction): Callback function of this Slash Command.  (Can be optional to set later - fetching from api)
        """
        self._callback: Optional[CoroutineFunction] = callback  # Register Callback function. Can be set later.
        self._application_id: int = applicationId
        self._id: int = id if isinstance(id, int) else 0
        self._name: str = name
        self._description: str = description if description is not None else ''

        # Parse options
        options: Optional[List[JSON]] = options if isinstance(options, collections.abc.Iterable) else []
        self._options: Optional[List[ApplicationCommandOption]] = []
        for option_json in options:
            self._options.append(ApplicationCommandOption(option_json))

        # Parse default option
        try:
            # Find default option
            self._defaultOption: ApplicationCommandOption = tuple(filter(
                    lambda opt: opt.option,
                    sorted(self._options, key=lambda opt: opt.name.lower())
                ))[0]
        except IndexError:
            # In case there is no default option
            self._defaultOption: Optional[ApplicationCommandOption] = None

    def invoke(self, *args, **kwargs) -> Coroutine[...]:
        """Safe call _func + patch additional hooks (check, before&after invoke)
        Returns:
            Coroutine object of callback function.
        """
        return await self._callback(*args, **kwargs)

    @property
    def id(self) -> int:
        return self._id

    @property
    def application_id(self) -> int:
        return self._application_id

    @application_id.setter
    def application_id(self, new: int) -> NoReturn:
        if isinstance(new, int):
            self._application_id = new
        else:
            raise TypeError('ApplicationCommand.application_id must be an integer!')

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def options(self) -> Tuple[ApplicationCommandOption]:
        return tuple(self._options)

    @property
    def defaultOption(self) -> Optional[ApplicationCommandOption]:
        return self._defaultOption

    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommand:
        return cls(**data)  # Set coro later.

    def toJson(self) -> JSON:
        data = {}
        data.update({'id': self._id})
        data.update({'application_id': self._application_id})
        data.update({'name': self._name})
        data.update({'description': self._description})
        data.update({'options': list(
            map(
                lambda opt: opt.toJson(),
                self._options
            )
        )})
        return data

    # Callback Helpers
    def callback(self) -> Callable[[CoroutineFunction], CoroutineFunction]:
        def wrapper(coro: CoroutineFunction) -> NoReturn:
            if not asyncio.iscoroutinefunction(coro):
                raise TypeError('Callback function must be coroutine function')
            self._callback = coro
            return coro

        return wrapper

    # Register Helpers
    async def _register(self) -> JSON:
        """Post Slash Command's JSON data to V5's Slash Command endpoint. (Slash Command Creation)
        Returns:
            interaction (JSON) data used in SlashCommand._patch to update initial information (id, ...)
        """
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=DiscordAPI().application(self._application_id).commands(self._id).url,
                    json=self._data
            ) as response:
                interaction: JSON = await response.json(encoding='utf-8')
                return interaction

    def _patch(self, interaction: JSON) -> NoReturn:
        """Patch interaction (response from discord api call) to SlashCommand.
        Args:
            interaction (JSON):
        """
        self._id = interaction['id']

        self._data.update(interaction)  # Update data.

    # Code-based creation
    @classmethod
    def create(
            cls,
            application_id: int,
            name: Optional[str] = None,
    ) -> Callable[[CoroutineFunction], ApplicationCommand]:
        """Create new Slash command.
        Args:
            application_id (int):
            name (str): Name of the Slash Command.
        Optional Args:
            **kwargs (Any): Additional attributes of Slash Command.
        :return:
        """

        def wrapper(coro: CoroutineFunction) -> ApplicationCommand:
            data = {
                'name': name if name is not None else coro.__name__
            }
            instance = cls(application_id, data, coro)
            createTask = asyncio.create_task(instance._register(), name=f'SlashCommand(name={name}).create')
            createTask.add_done_callback(instance._patch)
            return instance

        return wrapper

    async def edit(
            self,
            **kwargs
    ) -> NoReturn:
        async with aiohttp.ClientSession() as session:
            resp = await session.patch(
                url=DiscordAPI().application(self._application_id).commands(self._id).url,
                data=self.toJson()
            )
            resp_json: JSON = await resp.json()

    def subCommandGroup(self) -> ApplicationSubCommandGroup:
        pass

    def subCommand(self) -> ApplicationSubCommand:
        pass



