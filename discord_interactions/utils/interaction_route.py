from __future__ import annotations
from typing import ClassVar, Tuple, Final, Literal, Optional, Mapping, Iterable, Any, Union

import aiohttp
from aiohttp import BasicAuth, ClientTimeout, HttpVersion, BaseConnector
from aiohttp.typedefs import LooseHeaders, LooseCookies
from aiohttp.client import _SessionRequestContextManager
from aiohttp.http import HttpVersion11
from aiohttp.helpers import sentinel

# Constants
# Applications constants
from .type_hints import JSON
from .log import get_stream_logger, DEBUG

Applications: Final[str] = 'applications/'
ApplicationID: Final[str] = 'application_id'

# Guilds constants
Guilds: Final[str] = 'guilds/'
GuildID: Final[str] = 'guild_id'

# Command constants
Commands: Final[str] = 'commands/'
CommandID: Final[str] = 'command_id'

# Interactions constants
Interactions: Final[str] = 'interactions'
InteractionID: Final[str] = 'interaction_id'
InteractionToken: Final[str] = 'interaction_token'

# Webhooks constants
Webhooks: Final[str] = 'webhooks'
IsWebhook: Final[str] = 'is_webhook'

# Message constants
Messages: Final[str] = 'messages'
MessageID: Final[str] = 'message_id'

Endpoints: Final[Tuple[str, ...]] = (Applications, Guilds, Commands, Interactions, Webhooks, Messages)


logger = get_stream_logger('discord_interactions.utils', DEBUG)


class InteractionRoute:
    APIBase: ClassVar[str] = 'https://discord.com/api/v9/'

    # Supported combinations
    # Global commands:
    # 1. Create new command (post), Get all commands (get) :
    # /applications/{application.id}/commands
    # 2. Get single command (get), Edit single command (patch), Delete single command (delete) :
    # /applications/{application.id}/commands/{command.id}
    # Guild commands:
    # 1. Create new command (post), Get all commands (get) :
    # /applications/{application.id}/guilds/{guild.id}/commands
    # 2. Get single command (get), Edit single command (patch), Delete single command (delete) :
    # /applications/{application.id}/guilds/{guild.id}/commands/{command.id}

    def __init__(self):
        self._url = self.APIBase

    def _appendEndpointURL(self, endpoint: str, *params: Any) -> None:
        logger.debug('DEBUG: url appended with [endpoint: {}, params: {}]'.format(endpoint, params))
        url: str = (self.url if self.url.endswith('/') else self.url + '/') + '{}/'.format(endpoint)
        url += '/'.join(map(str, params))
        logger.debug('DEBUG: result > {}'.format(url))
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    @property
    def applicationID(self) -> Optional[int]:
        """
        Return 'application_id' stored in SlashRoute
        Returns:
            Optional[int] value of 'application_id'. None if 'application_id' is not set.
        """
        return getattr(self, ApplicationID, None)

    @applicationID.setter
    def applicationID(self, new: int) -> None:
        """
        Set 'application_id' attribute on SlashRoute.
        Args:
            new : application_id to set.
        """
        if not isinstance(new, int):
            raise TypeError('SlashRoute.applicationID must be an instance of integer.')
        setattr(self, ApplicationID, new)
        self._appendEndpointURL(Applications, new)

    @property
    def guildID(self) -> Optional[int]:
        """
        Return 'guild_id' stored in SlashRoute
        Returns:
            Optional[int] value of 'guild_id'. None if 'guild_id' is not set.
        """
        return getattr(self, GuildID, None)

    @guildID.setter
    def guildID(self, new: int) -> None:
        """
        Set 'guild_id' attribute on SlashRoute.
        Args:
            new : guild id to set.
        """
        if not isinstance(new, int):
            raise TypeError('SlashRoute.guildID must be an instance of integer.')
        setattr(self, GuildID, new)
        self._appendEndpointURL(Guilds, new)

    @property
    def commandID(self) -> Optional[int]:
        """
        Return 'command_id' stored in SlashRoute
        Returns:
            Optional[int] value of 'command_id'. None if 'command_id' is not set.
        """
        return getattr(self, GuildID, None)

    @commandID.setter
    def commandID(self, new: int) -> None:
        """
        Set 'command_id' attribute on SlashRoute.
        Args:
            new : command id to set.
        """
        if not isinstance(new, int):
            raise TypeError('SlashRoute.commandID must be an instance of integer.')
        setattr(self, CommandID, new)
        self._appendEndpointURL(Commands, new)

    @property
    def interactionID(self) -> Optional[int]:
        """
        Return 'interaction_id' stored in SlashRoute
        Returns:
            Optional[int] value of 'interaction_id'. None if 'interaction_id' is not set.
        """
        return getattr(self, InteractionID, None)

    @interactionID.setter
    def interactionID(self, new: int) -> None:
        """
        Set 'interaction_id' attribute on SlashRoute.
        Args:
            new : interaction id to set.
        """
        if not isinstance(new, int):
            raise TypeError('SlashRoute.interactionID must be an instance of integer.')
        setattr(self, InteractionID, new)
        self._appendEndpointURL(Interactions, new)

    @property
    def interactionToken(self) -> Optional[str]:
        return getattr(self, InteractionToken, None)

    @interactionToken.setter
    def interactionToken(self, new: str) -> None:
        """
        Set 'interaction_token' attribute on SlashRoute.
        Args:
            new : interaction token to set.
        """
        if not isinstance(new, str):
            raise TypeError('SlashRoute.interactionToken must be an instance of string.')
        setattr(self, InteractionToken, new)
        self._appendEndpointURL(Interactions, new)

    @property
    def isWebhook(self) -> bool:
        return getattr(self, IsWebhook, False)

    @isWebhook.setter
    def isWebhook(self, new: bool):
        if not isinstance(new, bool):
            raise TypeError('SlashRoute.isWebhook must be an instance of boolean.')
        setattr(self, IsWebhook, new)

    @property
    def messageID(self) -> Optional[Union[int, Literal['@original']]]:
        return getattr(self, MessageID, None)

    @messageID.setter
    def messageID(self, new: Union[int, Literal['@original']]) -> None:
        if new == '@original' or isinstance(new, int):
            setattr(self, MessageID, new)
            self._appendEndpointURL(Messages, new)
        else:
            raise TypeError("SlashRoute.messageID must be either '@original' or instance of integer.")

    # Route helpers
    def application(self, application_id: int) -> InteractionRoute:
        """Route for `/application` endpoint."""
        if getattr(self, ApplicationID, False):
            # application_id가 지정되어있으면 뒤에 application/ endpoint 를 붙일 수 없다.
            raise ValueError('Invalid position of application/ endpoint')
        self.applicationID = application_id
        return self     # Support method chaining

    def guilds(self, guild_id: int) -> InteractionRoute:
        """Route for`/application/guilds` endpoint."""
        if not getattr(self, ApplicationID, False) or getattr(self, GuildID, True):
            # application_id 가 지정되지 않았거나 guild_id 가 이미 지정되었을 경우 뒤에 guilds/ 엔드포인트를 붙일 수 없다.
            raise ValueError('Invalid position of guilds/ endpoint')
        self.guildID = guild_id
        return self     # Support method chaining

    def commands(self, command_id: Optional[int] = None) -> InteractionRoute:
        """Route for '/application/commands`, '/application/guilds/commands' endpoint."""
        if command_id is not None:
            if not getattr(self, 'application_id', False) and getattr(self, 'command_id', False):
                # application_id 가 지정되지 않았거나 command_id 가 이미 지정되었을 경우
                raise ValueError('Invalid position of commands/ endpoint')
            self.commandID = command_id
        else:
            self._url += '/commands'
        return self     # Support method chaining

    def interactions(self, interaction_id: int, interaction_token: str) -> InteractionRoute:
        """Route for `/interactions` endpoint."""
        if not getattr(self, InteractionID, False) and getattr(self, InteractionToken, False):
            # application_id 가 지정되지 않았거나 command_id 가 이미 지정되었을 경우
            raise ValueError('Invalid position of interactions/ endpoint')
        self.interactionID = interaction_id
        self.interactionToken = interaction_token
        return self     # Support method chaining

    def webhooks(self, application_id: int, interaction_token: str) -> InteractionRoute:
        self._appendEndpointURL(Webhooks, application_id)
        self.application(application_id).interactions(-1, interaction_token)    # TODO : -1 as interaction_id not set.
        return self     # Support method chaining

    def messages(self, message_id: Union[int, Literal['@original']] = '@original'):
        self._appendEndpointURL(Webhooks, message_id)

    # HTTP request (using aiohttp)

    def request(
            self,
            method: Literal['GET', 'POST', 'PATCH', 'DELETE'],
            *,
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: JSON = None,
            headers: Optional[LooseHeaders] = None,
            skip_auto_headers: Optional[Iterable[str]] = None,
            auth: Optional[BasicAuth] = None,
            allow_redirects: bool = True,
            max_redirects: int = 10,
            compress: Optional[str] = None,
            chunked: Optional[bool] = None,
            expect100: bool = False,
            raise_for_status: Optional[bool] = None,
            read_until_eof: bool = True,
            proxy: Optional[str] = None,
            proxy_auth: Optional[BasicAuth] = None,
            timeout: Union[ClientTimeout, object] = sentinel,
            cookies: Optional[LooseCookies] = None,
            version: HttpVersion = HttpVersion11,
            connector: Optional[BaseConnector] = None,
            read_bufsize: Optional[int] = None,
    ) -> _SessionRequestContextManager:
        """Send a http requestConstructs and sends a request. Returns response object.
        Args:
            method : HTTP method.
            params : Dictionary or bytes to be sent in the query string of the new request.
            data : Dictionary, bytes, or file-like object to send in the body of the request.
            json : Any json compatible python object.
            headers : Dictionary of HTTP Headers to send with the request.
            skip_auto_headers : Missing Docstring. Originated from aiohttp.request().
            auth : BasicAuth named tuple represent HTTP Basic Auth.
            allow_redirects : If set to False, do not follow redirects.
            max_redirects : Maximum limit of redirects.
            compress : Set to True if request has to be compressed with deflate encoding.
            chunked : Set to chunk size for chunked transfer encoding.
            expect100 : Expect 100-continue response from server.
            raise_for_status : Missing Docstring. Originated from aiohttp.request().
            read_until_eof : Read response until eof if response does not have Content-Length header.
            proxy : Missing Docstring. Originated from aiohttp.request().
            proxy_auth : Missing Docstring. Originated from aiohttp.request().
            timeout : Optional ClientTimeout settings structure, 5min total timeout by default.
            cookies : Dict object to send with the request.
            version : Request HTTP version.
            connector : BaseConnector sub-class instance to support connection pooling.
            read_bufsize : Missing Docstring. Originated from aiohttp.request().

        Returns:
            aiohttp.ClientResponse object containing response of the request.
        """
        return aiohttp.request(
            method=method,
            url=self.url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            skip_auto_headers=skip_auto_headers,
            auth=auth,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            compress=compress,
            chunked=chunked,
            expect100=expect100,
            raise_for_status=raise_for_status,
            read_until_eof=read_until_eof,
            proxy=proxy,
            proxy_auth=proxy_auth,
            timeout=timeout,
            cookies=cookies,
            version=version,
            connector=connector,
            read_bufsize=read_bufsize
        )

    def get(self, *args, **kwargs) -> _SessionRequestContextManager:
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs) -> _SessionRequestContextManager:
        return self.request('POST', *args, **kwargs)

    def patch(self, *args, **kwargs) -> _SessionRequestContextManager:
        return self.request('PATCH', *args, **kwargs)

    def delete(self, *args, **kwargs) -> _SessionRequestContextManager:
        return self.request('DELETE', *args, **kwargs)
