from abc import ABCMeta, abstractmethod
from typing import Callable, Optional, Any, NoReturn, Dict, Tuple, Union, List

from discord.ext.commands import Bot

from discord_slash.models.slash import ApplicationCommand, ApplicationCommandOption
from discord_slash.utils.type_hints import CoroutineFunction


# type hints
ApplicationCommandWrapper = Callable[..., ApplicationCommand]


class BaseApplication(metaclass=ABCMeta):
    """Abstract Base Class of Slash command clients"""
    def __init__(self) -> NoReturn:
        # Slash Command storage
        self.__application_commands__: Dict[str, ApplicationCommand] = {}

    @property
    def applicationCommands(self) -> Tuple[ApplicationCommand, ...]:
        return tuple(self.__application_commands__.values())

    @abstractmethod
    def globalSlash(
            self,
            name: str,
            description: str,
            **options: ApplicationCommandOption
    ) -> ApplicationCommandWrapper:
        """Wrap a coroutine function object into Global Slash Command instance"""
        ...

    slash = globalSlash     # Alias.

    @abstractmethod
    def guildSlash(
            self,
    ) -> ApplicationCommandWrapper:
        """

        :return:
        """
        ...


class SlashBot(Bot, BaseApplication):
    """Bot class supporting Slash Command features"""

    def __init__(
            self,
            command_prefix: Union[str, List[str]],
            description: str = None,
            help_command=None,
            **options: Any
    ) -> None:
        super().__init__(command_prefix, description, help_command, **options)
        self._applicationId: int = (await self.application_info()).id
        self.event(self.on_socket_response)     # Register event handler

    async def on_socket_response(self, msg: Any):
        """event handler for websocket's response.

        :param msg:
        :return:
        """
        print(msg)

    def slashCommand(
            self,
            name: str,
            description: str
    ) -> Callable[..., Callable[[CoroutineFunction], ApplicationCommand]]:
        """
        :param name:
        :param description:
        :return:
        """

    slash = slashCommand    # Alias

    def guildSlashCommand(
            self,
            name: Optional[str] = None,
            description: Optional[str] = None
    ) -> Callable[..., Callable[[CoroutineFunction], ApplicationCommand]]:
        """

        """
        def wrapper(coro: CoroutineFunction) -> ApplicationCommand:
            command = ApplicationCommand(

            )
            return command

        return wrapper

    guildSlash = guildSlashCommand  # Alias


SlashClient = SlashBot  # Alias