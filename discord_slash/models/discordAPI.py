from __future__ import annotations
from typing import ClassVar, Tuple


class DiscordAPI:
    APIBase: ClassVar[str] = 'https://discord.com/api/v8/'

    # Applications constants
    Applications: ClassVar[str] = 'applications/'
    ApplicationID: ClassVar[str] = 'application_id'

    # Users constants
    Users: ClassVar[str] = 'users/'
    UserID: ClassVar[str] = 'user_id'

    # Guilds constants
    Guilds: ClassVar[str] = 'guilds/'
    GuildID: ClassVar[str] = 'guild_id'

    # Command constants
    Commands: ClassVar[str] = 'commands/'
    CommandID: ClassVar[str] = 'command_id'

    Endpoints: ClassVar[Tuple[str]] = (Applications, Users, Guilds, Commands)

    def __init__(self):
        self._url = self.APIBase

    def _generateParamsUrl(self, endpoint: str, *args) -> str:
        url: str = endpoint
        if not endpoint.endswith('/'):
            url += '/'
        for arg in args:
            url += f'{arg}/'
        
        return url

    @property
    def url(self) -> str:
        return self._url

    def user(self, user_id: int):
        """Route for `/users` endpoint."""
        if self._url != self.APIBase:
            raise ValueError('Invalid position of users/ endpoint')
        setattr(self, self.UserID, user_id)
        self._url += self._generateParamsUrl(self.Users, user_id)

    def guilds(self, guild_id: int):
        """Route for `/guilds`, `/application/guilds` endpoint."""
        if self._url != self.APIBase or getattr() not in self._url:
            raise ValueError('Invalid position of guilds/ endpoint')
        setattr(self, self.GuildID, guild_id)
        self._url += self._generateParamsUrl(self.Guilds, guild_id)

    def application(self, application_id: int) -> DiscordAPI:
        """Route for `/application` endpoint."""
        if self._url != self.APIBase:
            raise ValueError('Invalid position of application/ endpoint')
        setattr(self, self.ApplicationID, application_id)
        self._url += self._generateParamsUrl(self.Applications, application_id)
        return self # For method chaining

    def commands(self, command_id: int):
        """Route for `/application/commands` endpoint."""
        if not getattr(self, 'application_id', False) and getattr(self, 'command_id', False):
            # applcation_id 는 지정되었지만 command_id 는 지정되지 않았을 경우
            raise ValueError('Invalid position of commands/ endpoint')
        setattr(self, self.CommandID, command_id)
        self._url += self._generateParamsUrl(self.Commands, command_id)

    @classmethod
    def getGlobalCommandEndpoint(cls, application_id: int) -> str:
        return cls().application(application_id).url + cls.Commands

    @classmethod
    def getGuildCommandEndpoint(cls, application_id: int, guild_id: int) -> str:
        return cls().application(application_id).guilds(guild_id).url + cls.Commands

    def __divmod__(self, other) -> str:
        if isinstance(other, str):
            return self.url + '/' + other


        raise TypeError('Cannot use division operator / with given type {}'.format(type(other)))






