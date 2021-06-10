import asyncio
import inspect
from typing import Callable, Optional, Any, Dict, Tuple, Union, List

from discord.ext.commands.bot import BotBase
from discord import Client, AutoShardedClient

from discord_interactions.application_commands.models import ApplicationCommand, ApplicationCommandOption, Interaction
from discord_interactions.utils.type_hints import CoroutineFunction, JSON

# type hints
ApplicationCommandWrapper = Callable[..., ApplicationCommand]


__all__ = (
    'SlashClient',
    'AutoShardedSlashClient',
    'SlashBot',
    'AutoShardedSlashBot'
)


class BaseSlashApplication:
    """Base Class of Slash command clients"""
    def __init__(self, application_id: int = 0) -> None:
        # Slash Command storage
        self.__application_commands__: Dict[int, ApplicationCommand] = {}
        self._application_id: int = application_id

    @property
    def application_id(self) -> int:
        return self._application_id

    @application_id.setter
    def application_id(self, new: int) -> None:
        if not isinstance(new, int):
            raise TypeError('[discord_interactions] BaseApplication.application_id must be integer value!')
        self._application_id = new

    @property
    def applicationCommands(self) -> Tuple[ApplicationCommand, ...]:
        return tuple(self.__application_commands__.values())

    def getCommand(self, command_id: int) -> Optional[ApplicationCommand]:
        return self.__application_commands__.get(command_id)

    def get_command_by_name(self, name: str) -> Optional[ApplicationCommand]:
        return next(filter(
            lambda c: c.name == name,
            self.__application_commands__.values()
        ))

    async def process_slash(self, data: JSON):
        """
        Process slash commands with given socket response.

        Args:
            data (JSON): Gateway message.
        """
        interaction: Interaction = Interaction.fromJson(data)
        command: ApplicationCommand = interaction.getCommand(client=self)
        await command.invoke()

    def __createSlash(
            self,
            application_id: int,
            name: str,
            description: str,
            options: Optional[List[Union[ApplicationCommandOption, JSON]]] = None,
            callback: Optional[CoroutineFunction] = None,
            is_guild_command: bool = False,
            guild_id: Optional[int] = None
    ) -> ApplicationCommand:

        parsed_options: List[ApplicationCommandOption] = list(map(
            lambda o: o if isinstance(o, ApplicationCommandOption) else ApplicationCommandOption.fromJson(o),
            options
        ))

        if is_guild_command:
            command = ApplicationCommand(
                application_id=application_id,
                name=name,
                description=description,
                options=options,
                callback=callback,
                guild_id=guild_id
            )
        else:
            return ApplicationCommand(
                application_id=application_id,
                name=name,
                description=description,
                options=options,
                callback=callback
            )
        self.__application_commands__.update({command.id: command})
        return command

    def globalSlash(
            self,
            name: Optional[str],
            description: Optional[str] = None,  # If None, read from docstring.
            options: Optional[List[Union[ApplicationCommandOption, JSON]]] = None
    ) -> Callable[[CoroutineFunction], ApplicationCommand]:
        """
        Create and register ApplicationCommand object

        Args:
            name (str):
            description (Optional[str]):
            options (Optional[List[Union[ApplicationCommandOption, JSON]]]:

        Returns:
            Created ApplicationCommand object.
        """

        def wrapper(coro: CoroutineFunction) -> ApplicationCommand:
            if not asyncio.iscoroutinefunction(coro):
                raise TypeError("Callback function of ApplicationCommand must be a coroutine function!")

            command_name = name if name is not None else coro.__name__
            command_description = description if description is not None else inspect.getdoc(coro)  # Use inspect.getdoc() to clean code block indentation.

            command = self.__createSlash(
                application_id=self.application_id,
                name=command_name,
                description=command_description,
                options=options,
                callback=coro,
                is_guild_command=False
            )

            return command
        return wrapper

    slash = globalSlash     # Alias

    def guildSlashCommand(
            self,
            guild_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None,
            options: Optional[List[Union[ApplicationCommandOption, JSON]]] = None
    ) -> Callable[[CoroutineFunction], ApplicationCommand]:
        """
        Create and register ApplicationCommand object

        Args:
            guild_id (int): guild id to create slash command.
            name (str): name of the slash command.
            description (Optional[str]): description of the slash command
            options (Optional[List[Union[ApplicationCommandOption, JSON]]: options of the slash command.

        Returns:
            Created ApplicationCommand object.
        """

        def wrapper(coro: CoroutineFunction) -> ApplicationCommand:
            if not asyncio.iscoroutinefunction(coro):
                raise TypeError("Callback function of ApplicationCommand must be a coroutine function!")

            command_name = name if name is not None else coro.__name__
            command_description = description if description is not None else inspect.getdoc(coro)  # Use inspect.getdoc() to clean code block indentation.

            command = self.__createSlash(
                name=command_name,
                description=command_description,
                application_id=self._application_id,
                options=options,
                callback=coro,
                is_guild_command=True,
                guild_id=guild_id
            )

            return command
        return wrapper


class SlashClient(Client, BaseSlashApplication):
    """Client class supporting Slash Command features"""

    def __init__(self, **options):
        super(SlashClient, self).__init__(**options)

        async def get_application_id():
            self.application_id = (await self.application_info()).id

        self.loop.create_task(
            get_application_id(),
            name='SlashClient.get_application_id'
        )

    async def on_socket_response(self, msg: JSON):
        """
        Event handler for websocket response.

        Args:
            msg (JSON): Gateway message.
        """
        # Temporary debug code for future development
        print(f'[on_socket_response]msg={msg}')

        if msg['op'] != 0 or msg['t'] != 'INTERACTION_CREATE':
            # Not a slash command related websocket response.
            return

        return await self.process_slash(msg['d'])


class AutoShardedSlashClient(AutoShardedClient, BaseSlashApplication):
    """AutoSharded version of SlashClient."""

    def __init__(self, *args, loop=None, **kwargs):
        super().__init__(*args, loop=loop, **kwargs)

        async def get_application_id():
            self.application_id = (await self.application_info()).id

        self.loop.create_task(
            get_application_id(),
            name='SlashClient.get_application_id'
        )

    async def on_socket_response(self, msg: Any):
        """Event handler for websocket response.
        Args:
            msg (Any): socket response
        """
        # Temporary debug code for future development
        print(f'[on_socket_response]msg={msg}')
        await self.process_slash(msg)


class SlashBot(BotBase, SlashClient):
    """Bot class supporting Slash Command features"""

    def __init__(
            self,
            command_prefix: Union[str, List[str]],
            description: str = None,
            help_command=None,
            **options: Any
    ) -> None:
        super().__init__(command_prefix, description, help_command, **options)


class AutoShardedSlashBot(SlashBot, AutoShardedClient):
    """
    Auto-sharding slash client.
    """
    def __init__(self):
        super().__init__()
    pass
