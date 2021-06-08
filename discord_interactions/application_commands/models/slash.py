from __future__ import annotations

import asyncio
import collections
import logging
import types
from enum import IntFlag, Enum
from typing import Union, Optional, List, Callable, Coroutine, NoReturn, Tuple, Any, Dict

import aiohttp
from discord import Member, Guild, TextChannel, User, Message, File

from discord_interactions.utils.type_hints import JSON, CoroutineFunction
from discord_interactions.utils.abstracts import JsonObject
from discord_interactions.utils.slash_route import SlashRoute
from discord_interactions.utils.exfend_builtins import Filter, Compute

__all__ = (
    'InteractionType',
    'ApplicationCommandInteractionData',
    'ApplicationCommandInteractionDataOption',
    'Interaction',
    'InteractionResponseType',
    'InteractionResponseFlags',
    'InteractionResponse',
    'ApplicationCommand', 'SlashCommand',
    'ApplicationCommandOption', 'SlashCommandOption',
    'ApplicationCommandOptionType', 'SlashCommandOptionType',
    'ApplicationSubCommand', 'SlashSubCommand',
    'ApplicationSubCommandGroup', 'SlashSubCommandGroup',
    'ApplicationCommandOptionChoice', 'SlashCommandOptionChoice',
    'SlashContext'
)


slash_logger: logging.Logger = logging.getLogger('discord_interactions')


class InteractionType(Enum):
    PING = 1
    APPLICATION_COMMAND = 2

    @classmethod
    def parse(cls, value: int) -> Optional[InteractionType]:
        return Filter(lambda m: m.value == value, cls.__members__.values()).findFirst()


class ApplicationCommandInteractionDataOption(JsonObject):
    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommandInteractionDataOption:
        value = data.get('value')
        raw_option = data.get('option')
        if value is not None and raw_option is not None:
            raise ValueError('ApplicationCommandInteractionDataOption cannot have both value and option.')

        option = ApplicationCommandInteractionDataOption.fromJson(raw_option) if raw_option is not None else None

        return cls(
            name=data['name'],
            value=value,
            option=option
        )

    def __init__(
        self,
        name: str,
        value: Optional[Any] = None,
        option: Optional[List[ApplicationCommandInteractionDataOption]] = None
    ) -> None:
        self._name: str = name
        self._value: Optional[Any] = value
        self._option: Optional[List[ApplicationCommandInteractionDataOption]] = option

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Any:
        return self._value

    @property
    def option(self) -> Optional[List[ApplicationCommandInteractionDataOption]]:
        return self._option

    def toJson(self) -> JSON:
        data = {'name': self._name}
        if self._value is not None:
            data.update(value=self._value)

        if self._option is not None:
            data.update(option=[o.toJson() for o in self._option])


class ApplicationCommandInteractionData(JsonObject):
    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommandInteractionData:
        return cls(
            command_id=data['id'],
            name=data['name'],
            options=data.get('options')
        )

    def __init__(
        self,
        command_id: int,
        name: str,
        options: Optional[List[ApplicationCommandInteractionDataOption]] = None
    ):
        self._id: int = command_id
        self._name: str = name
        self._options: Optional[List[ApplicationCommandInteractionDataOption]] = options

    def getOptions(self) -> Optional[Dict[str, ApplicationCommandInteractionDataOption]]:
        if self._options is not None:
            options_map = {}
            # TODO : Implement command invoke logic.
            # TODO : Finish parsing options of interaction to Dict[str, ApplicationCommandInteractionDataOption] s
            Compute(
                lambda o: options_map.update(
                    {o: o}
                ),
                self._options
            ).run()
        else:
            return None

    def toJson(self) -> JSON:
        data = {}
        data.update(
            id=self._id,
            name=self._name
        )
        if self._options is not None:
            data.update(options=[o.toJson() for o in self._options])

        return data


class Interaction(JsonObject):
    """
    Interaction object.
    Example :
    {
        "type": 2,
        "token": "A_UNIQUE_TOKEN",
        "member": {
            "user": {
                "id": 53908232506183680,
                "username": "Mason",
                "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
                "discriminator": "1337",
                "public_flags": 131141
            },
            "roles": ["539082325061836999"],
            "premium_since": null,
            "permissions": "2147483647",
            "pending": false,
            "nick": null,
            "mute": false,
            "joined_at": "2017-03-13T19:19:14.040000+00:00",
            "is_pending": false,
            "deaf": false
        },
        "id": "786008729715212338",
        "guild_id": "290926798626357999",
        "data": {
            "options": [{
                "name": "cardname",
                "value": "The Gitrog Monster"
            }],
            "name": "cardsearch",
            "id": "771825006014889984"
        },
        "channel_id": "645027906669510667"
    }

    """

    @classmethod
    def fromJson(cls, data: JSON) -> Interaction:
        if not isinstance(data, types.MappingProxyType):
            raise TypeError('ApplicationCommandOptionChoice.fromJson() expects json data, not {}.'.format(type(data)))
        raw_member: JSON = data['member']
        return cls(
            interaction_type=InteractionType.parse(data['type']),
            interaction_id=data['id'],
            guild_id=data['guild_id'],
            channel_id=data['channel_id'],
            raw_member=raw_member,
            token=data['token'],
            application_command_data=data['data']
        )

    def __init__(
        self,
        # Common properties
        interaction_type: InteractionType,
        interaction_id: int,
        guild_id: int,
        channel_id: int,
        raw_member: JSON,
        token: str,
        version: int,
        # Optional properties
        application_command_data: Optional[ApplicationCommandInteractionData] = None
    ) -> None:
        self._id: int = interaction_id
        self._type: InteractionType = interaction_type
        self._guild_id: int = guild_id
        self._channel_id: int = channel_id
        self._member_id: int = raw_member['user']['id']
        self._raw_member: JSON = raw_member
        self._token: str = token
        self._version: int = version
        self._application_command_data: Optional[ApplicationCommandInteractionData] = application_command_data

    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> InteractionType:
        return self._type

    @property
    def guild_id(self) -> int:
        return self._guild_id

    @property
    def channel_id(self) -> int:
        return self._channel_id

    @property
    def member_id(self) -> int:
        return self._member_id

    @property
    def raw_member(self) -> JSON:
        return self._raw_member

    @property
    def version(self) -> int:
        return self._version

    def getCommand(self, client) -> Optional[ApplicationCommand]:
        """
        "data": {
            "options": [{
                "name": "cardname",
                "value": "The Gitrog Monster"
            }],
            "name": "cardsearch",
            "id": "771825006014889984"
        }

        Args:
            client (BaseApplication): Slash client currently running.

        Returns:
            Parsed ApplicationCommand object.
        """
        command = client.getCommand(self._id)

        return command

    def _parseOptions(self) -> Optional[List[ApplicationCommandOption]]:
        self._application_command_data.get('options')

    async def respond(
        self,
        response: InteractionResponse
    ):
        url = 'https://discord.com/api/v8/interactions/{0}/{1}/callback'.format(self._id, self._token)
        async with aiohttp.ClientSession() as s:
            async with s.post(
                url,
                json=response.toJson()
            ) as resp:
                pass

    def toJson(self) -> JSON:
        """
        {
            "type": 2,
            "token": "A_UNIQUE_TOKEN",
            "member": {
                "user": {
                    "id": 53908232506183680,
                    "username": "Mason",
                    "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
                    "discriminator": "1337",
                    "public_flags": 131141
                },
                "roles": ["539082325061836999"],
                "premium_since": null,
                "permissions": "2147483647",
                "pending": false,
                "nick": null,
                "mute": false,
                "joined_at": "2017-03-13T19:19:14.040000+00:00",
                "is_pending": false,
                "deaf": false
            },
            "id": "786008729715212338",
            "guild_id": "290926798626357999",
            "data": {
                "options": [{
                    "name": "cardname",
                    "value": "The Gitrog Monster"
                }],
                "name": "cardsearch",
                "id": "771825006014889984"
            },
            "channel_id": "645027906669510667"
        }
        :return:
        """
        data = {}
        data.update(
            type=self._type.value,
            token=self._token,
            member=self._raw_member,
            id=self._id,
            guild_id=self._guild_id,
            data=self._application_command_data,
            channel_id=self._channel_id
        )
        return data


class InteractionResponseType(Enum):
    PONG = 1
    ACKNOWLEDGE = 2
    CHANNEL_MESSAGE = 3
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    ACKNOWLEDGE_WITH_SOURCE = 5

    @classmethod
    def parse(cls, value: int) -> InteractionResponseType:
        return Filter(lambda m: m.value == value, cls.__members__.values()).findFirst()


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


class InteractionResponse(JsonObject):
    # TODO : Finish InteractionResponse model
    # TODO : Finish Interaction Response sending logic on command invoke
    @classmethod
    def fromJson(cls, data: JSON) -> InteractionResponse:
        return cls(

        )

    def __init__(
        self,
        response_type: InteractionResponseType,
        response_flags: Optional[List[InteractionResponseFlags]] = None
    ) -> None:
        pass

    def toJson(self) -> JSON:
        data = {}
        return data


class ApplicationCommandOptionChoice(JsonObject):

    @classmethod
    def fromJson(cls, data: JSON) -> SlashCommandOptionChoice:
        if not isinstance(data, types.MappingProxyType):
            raise TypeError('ApplicationCommandOptionChoice.fromJson() expects json data, not {}.'.format(type(data)))
        return cls(name=data['name'], value=data['value'])

    def __init__(self, name: str, value: Union[str, int]) -> None:
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Union[str, int]:
        return self._value

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
    def parse(cls, value) -> ApplicationCommandOptionType:
        print(cls.__members__.values())
        return tuple(filter(lambda m: m.value == value, cls.__members__.values()))[0]


SlashCommandOptionType = ApplicationCommandOptionType  # Alias


class ApplicationCommandOption(JsonObject):
    """
    # object structure (json)
    type	    int	                                    value of ApplicationCommandOptionType
    name	    string	                                1-32 character name
    description	string	                                1-100 character description
    default?	bool	                                the first required option for the user to complete--only one option can be default
    required?	bool	                                if the parameter is required or optional--default false
    choices?	array of ApplicationCommandOptionChoice	choices for string and int types for the user to pick from
    options?	array of ApplicationCommandOption	    if the option is a subcommand or subcommand group type, this nested options will be the parameters

    # example command option object
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

    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommandOption:
        # TODO : Maybe OptionType check can be occurred in fromJson to reduce time cost when invalid parameters are passed?
        if not isinstance(data, types.MappingProxyType):
            raise TypeError('ApplicationCommandOption.fromJson() expects json data, not {}.'.format(type(data)))

        raw_choices: Optional[List[JSON]] = data.get('choices')
        choices: Optional[List[ApplicationCommandOptionChoice]] = None
        if raw_choices is not None:
            choices: List[ApplicationCommandOptionChoice] = []
            for raw_choice in raw_choices:
                choices.append(ApplicationCommandOptionChoice.fromJson(raw_choice))

        raw_options: Optional[List[JSON]] = data.get('options')
        options: Optional[List[ApplicationCommandOption]] = None
        if raw_options is not None:
            options: List[ApplicationCommandOption] = []
            for raw_option in raw_options:
                options.append(ApplicationCommandOption.fromJson(raw_option))

        return cls(
            name=data['name'],
            option_type=ApplicationCommandOptionType.parse(data['type']),
            description=data['description'],
            default=data.get('default'),
            required=data.get('required'),
            choices=choices,
            options=options
        )

    def __init__(
        self,
        name: str,
        option_type: ApplicationCommandOptionType,
        description: str = None,
        default: bool = False,
        required: bool = False,
        choices: Optional[List[ApplicationCommandOptionChoice]] = None,
        options: Optional[List[ApplicationCommandOption]] = None
    ) -> None:
        self._name: str = name
        self._type: ApplicationCommandOptionType = option_type
        self._description: str = description
        self._default = default
        self._required = required

        # check choices
        if choices is not None:
            if self._type != ApplicationCommandOptionType.STRING and self._type != ApplicationCommandOptionType.INTEGER:
                raise ValueError('Only commands with String and Integer CommandOptionType can have choices.')

            self.choices = tuple(choices)
        else:
            self.choices = None

        # check options
        if options is not None:
            if self._type != ApplicationCommandOptionType.SUB_COMMAND and self._type != ApplicationCommandOptionType.SUB_COMMAND_GROUP:
                raise ValueError(
                    'Only commands with SUB_COMMAND and SUB_COMMAND_GROUP CommandOptionType can have options.')

            self.options = tuple(options)
        else:
            self.options = None

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
        data = {}
        data.update({'name': self._name})
        data.update({'type': self._type.value})
        data.update({'description': self._description})


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

    # example command creation payload
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

    @classmethod
    def fromJson(cls, data: JSON) -> ApplicationCommand:
        """Parse Slash Command object from json data.
        Args:
            data (JSON): JSON value of the Slash Command.
            {
                'id': <int: id of ApplicationCommand>,
                'application_id': <int: id of discord application where this command is registered>
                'name': <str: name of the command>,
                'description': <str: description of the command>,
                'options': <list: array of command option json (up to 10)>
            }
        """
        return cls(
            # Required parameters
            name=data['name'],
            description=data['description'],
            # Optional Parameters
            command_id=data.get('id'),  # Optional on code-based creation. When retrieved on http api, must exist.
            application_id=data.get('application_id'),
            options=data.get('options')
        )

    def __init__(
            self,
            application_id: int,
            name: str,
            description: str = '',
            command_id: Optional[int] = None,   # Can be set later : code-based creation
            options: Optional[List[Union[ApplicationCommandOption, JSON]]] = None,  # Options are selective argument.
            guild_id: Optional[int] = None,     # Only required to make guild-specific slash commands
            callback: Optional[CoroutineFunction] = None    # Callback functions can be set later (when fetching existing slash commands from api)
    ):
        """Initialize Slash Command object. Must be called in SlashCommand.create()
        Args:
            name (str): name of the command
            description (Optional[str]): description of the command
            command_id (Optional[int]): id of ApplicationCommand
            application_id (int): id of V5 Application where this Slash Command is registered.
            callback (CoroutineFunction): Callback function of this Slash Command.  (Can be optional to set later - fetching from api)
        """
        self._callback: Optional[CoroutineFunction] = callback  # Register Callback function. Can be set later.
        # if application_id is None:
        #     raise ValueError("ApplicationCommand.application_id must be integer value of the application's snowflake id.")
        self._application_id: int = application_id  # Application's id where the application command is registered in.
        self._id: Optional[int] = command_id  # Id of the application command object. Will be retrieved from Discord's HTTP endpoint.
        self._name: str = name
        self._description: str = description if description is not None else ''

        # Guild-specific Application Command
        if guild_id is not None:
            self.__guild_command__: bool = True
            self._guild_id: int = guild_id if isinstance(guild_id, int) else 0
        else:
            self.__guild_command__: bool = False

        # Parse options
        options: Optional[List[JSON]] = options if isinstance(options, collections.abc.Iterable) else []
        self._options: Optional[List[ApplicationCommandOption]] = []
        for option_json in options:
            self._options.append(ApplicationCommandOption.fromJson(option_json))

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, new) -> None:
        if isinstance(new, int):
            self._id = new
        else:
            raise TypeError('ApplicationCommand.id must be an integer!')

    @property
    def application_id(self) -> int:
        return self._application_id

    @application_id.setter
    def application_id(self, new: int) -> None:
        if isinstance(new, int):
            self._application_id = new
        else:
            raise TypeError('ApplicationCommand.application_id must be an integer!')

    @property
    def isGuildCommand(self) -> bool:
        return self.__guild_command__

    @property
    def guild_id(self) -> Optional[int]:
        return self._guild_id

    @guild_id.setter
    def guild_id(self, new: int) -> None:
        if isinstance(new, int):
            self._guild_id = new
        else:
            raise TypeError('ApplicationCommand.guild_id must be an integer!')

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
        # Find default option
        return Filter(
            lambda opt: opt.option,
            sorted(self._options, key=lambda opt: opt.name.lower())
        ).findFirst()

    @property
    def before_invoke_hook(self) -> Optional[CoroutineFunction]:
        return getattr(self, 'before_invoke', None)

    @before_invoke_hook.setter
    def before_invoke_hook(self, coro: CoroutineFunction):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('Command invoke hooks must be a coroutine function!')
        setattr(self, 'before_invoke', coro)

    @property
    def after_invoke_hook(self) -> Optional[CoroutineFunction]:
        return getattr(self, 'after_invoke', None)

    @after_invoke_hook.setter
    def after_invoke_hook(self, coro: CoroutineFunction):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('Command invoke hooks must be a coroutine function!')
        setattr(self, 'after_invoke', coro)

    def before_invoke(self, coro: CoroutineFunction) -> CoroutineFunction:
        self.before_invoke_hook = coro

        return coro

    def after_invoke(self, coro: CoroutineFunction) -> CoroutineFunction:
        self.after_invoke_hook = coro

        return coro

    async def invoke(self, *args, **kwargs) -> None:
        """Safe call _func + patch additional hooks (check, before&after invoke)
        Returns:
            Coroutine object of callback function.
        """
        before_invoke = getattr(self, 'before_invoke', False)
        if before_invoke:
            await before_invoke()
        result = await self._callback(*args, **kwargs)
        after_invoke = getattr(self, 'after_invoke', False)
        if after_invoke:
            await after_invoke()

    def toJson(self) -> JSON:
        data = {}
        data.update({'id': self._id})
        data.update({'application_id': self._application_id})
        data.update({'name': self._name})
        data.update({'description': self._description})
        data.update({'options': list(map(
            lambda opt: opt.toJson(),
            self._options
        ))})
        return data

    # Callback Helpers
    def setCallback(self) -> Callable[[CoroutineFunction], CoroutineFunction]:
        """
        Returns:

        Returns:
            wrapper function which receive coroutine function and set
        """
        def wrapper(coro: CoroutineFunction) -> NoReturn:
            """
            Set command's callback function to given coroutine function object.
            Args:
                coro (coroutine function): coroutine function object to be used as command's callback.
            """
            if not asyncio.iscoroutinefunction(coro):
                raise TypeError('Callback function must be coroutine function')
            self._callback = coro
            return coro

        return wrapper

    # Register Helpers
    async def _register_command(self) -> JSON:
        """Post Slash Command's JSON data to V5's Slash Command endpoint. (Slash Command Creation)
        Returns:
            interaction (JSON) data used in SlashCommand._patch to update initial information (id, ...)
        """
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=SlashRoute().application(self._application_id).commands(self._id).url,
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
            description: Optional[str] = None
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
                url=SlashRoute().application(self._application_id).commands(self._id).url,
                data=self.toJson()
            )
            resp_json: JSON = await resp.json()

    def subCommandGroup(self) -> ApplicationSubCommandGroup:
        pass

    def subCommand(self) -> ApplicationSubCommand:
        pass


SlashCommand = ApplicationCommand   # Alias


class SlashContext:
    """Context object similar with Context in discord.ext.commands (currently targeting on discord.py)"""
    @classmethod
    async def fromInteraction(cls, client, interaction: Interaction) -> SlashContext:
        guild: Optional[Guild] = client.get_guild(interaction.guild_id)
        if guild is not None:
            channel: Optional[TextChannel] = guild.get_channel(interaction.channel_id)
            if channel is None:
                await guild.fetch_channels()
            author: Optional[Member] = guild.get_member(interaction.member_id)

            if channel is not None and author is not None:
                return cls(client, author, guild, channel, command)

    def __init__(
        self,
        client,
        author: Union[User, Member],
        guild: Guild,
        channel: TextChannel,
        command: ApplicationCommand
    ):
        self._client = client
        self._author: Member = author
        self._guild: Guild = guild
        self._channel: TextChannel = channel
        self._command: ApplicationCommand = command

    @property
    def client(self):
        return self._client

    @property
    def author(self) -> Union[User, Member]:
        return self._author

    @property
    def guild(self) -> Optional[Guild]:
        return self._guild

    @property
    def channel(self) -> Optional[TextChannel]:
        return self._channel

    async def send(self, *args, **kwargs) -> Message:
        # TODO : Think about file send. Use discord.py's implementation? (discord.File)
        pass

    async def edit(self, *args, **kwargs) -> None:
        pass
