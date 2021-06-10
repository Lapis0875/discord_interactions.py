import json
from logging import getLogger
from typing import List, Union, Optional

import discord
from discord import AllowedMentions, InvalidArgument, File, utils
from discord.abc import Messageable
from discord.http import HTTPClient, Route

# Backups
from discord_interactions.utils.type_hints import JSON
from .components import ComponentType, Component, ActionRow, Button
from .message import ComponentMessage

btn_logger = getLogger('discord_buttons')

Messageable_send = Messageable.send
HTTTPClient_send_message = HTTPClient.send_message
Route_BASE = Route.BASE


def parse_components_from_json(data: JSON) -> List[Component]:
    pass


def parse_components_into_json(components: List[Component]) -> List[Component]:
    pass


# Replace methods
# 'send' method in 'discord.abc.Messageable'
async def send(
        self: discord.abc.Messageable,
        content: str = None,
        *,
        tts: bool = False,
        embed: discord.Embed = None,
        file: discord.File = None,
        files: List[discord.File] = None,
        delete_after: float = None,
        nonce: int = None,
        allowed_mentions: discord.AllowedMentions = None,
        reference: Union[discord.Message, discord.MessageReference] = None,
        mention_author: Optional[bool] = None,
        components: List[Component] = None
) -> ComponentMessage:
    """|coro|

            Sends a message to the destination with the content given.
            This replaces original implementation of 'discord.abc.Messageable.send' to support discord buttons feature.

            The content must be a type that can convert to a string through ``str(content)``.
            If the content is set to ``None`` (the default), then the ``embed`` parameter must
            be provided.

            To upload a single file, the ``file`` parameter should be used with a
            single :class:`~discord.File` object. To upload multiple files, the ``files``
            parameter should be used with a :class:`list` of :class:`~discord.File` objects.
            **Specifying both parameters will lead to an exception**.

            If the ``embed`` parameter is provided, it must be of type :class:`~discord.Embed` and
            it must be a rich embed type.

            Parameters
            ------------
            # Originated from discord.py
            content: :class:`str`
                The content of the message to send.
            tts: :class:`bool`
                Indicates if the message should be sent using text-to-speech.
            embed: :class:`~discord.Embed`
                The rich embed for the content.
            file: :class:`~discord.File`
                The file to upload.
            files: List[:class:`~discord.File`]
                A list of files to upload. Must be a maximum of 10.
            nonce: :class:`int`
                The nonce to use for sending this message. If the message was successfully sent,
                then the message will have a nonce with this value.
            delete_after: :class:`float`
                If provided, the number of seconds to wait in the background
                before deleting the message we just sent. If the deletion fails,
                then it is silently ignored.
            allowed_mentions: :class:`~discord.AllowedMentions`
                Controls the mentions being processed in this message. If this is
                passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
                The merging behaviour only overrides attributes that have been explicitly passed
                to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
                If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
                are used instead.

            reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`]
                A reference to the :class:`~discord.Message` to which you are replying, this can be created using
                :meth:`~discord.Message.to_reference` or passed directly as a :class:`~discord.Message`. You can control
                whether this mentions the author of the referenced message using the :attr:`~discord.AllowedMentions.replied_user`
                attribute of ``allowed_mentions`` or by setting ``mention_author``.

            mention_author: Optional[:class:`bool`]
                If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.

            # New parameters added in discord_buttons
            components: Optional[List[:class:'~discord_buttons.Button']]
                List of Button objects to send with message.

            Raises
            --------
            ~discord.HTTPException
                Sending the message failed.
            ~discord.Forbidden
                You do not have the proper permissions to send the message.
            ~discord.InvalidArgument
                The ``files`` list is not of the appropriate size,
                you specified both ``file`` and ``files``,
                or the ``reference`` object is not a :class:`~discord.Message`
                or :class:`~discord.MessageReference`.

            Returns
            ---------
            :class:`~discord.Message`
                The message that was sent.
    """

    channel = await self._get_channel()
    state = self._state
    content = str(content) if content is not None else None
    if embed is not None:
        embed = embed.to_dict()

    if allowed_mentions is not None:
        if state.allowed_mentions is not None:
            allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
        else:
            allowed_mentions = allowed_mentions.to_dict()
    else:
        allowed_mentions = state.allowed_mentions and state.allowed_mentions.to_dict()

    if mention_author is not None:
        allowed_mentions = allowed_mentions or AllowedMentions().to_dict()
        allowed_mentions['replied_user'] = bool(mention_author)

    if reference is not None:
        try:
            reference = reference.to_message_reference_dict()
        except AttributeError:
            raise InvalidArgument('reference parameter must be Message or MessageReference') from None

    # Added in discord_buttons to support discord buttons feature.
    # buttons : Union[List[Button], Button]
    parsed_components: List[JSON] = []
    if components is not None:
        btn_logger.debug(
            'discord.abc.Messageable.send#patched > Parsing components : (type: {}) {}'.format(type(components),
                                                                                               components))
        if isinstance(components, ActionRow):
            parsed_components = [components.to_json()]

        elif isinstance(components, (list, tuple)):
            if isinstance(components[0], Component):
                if components[0].type != ComponentType.Container:
                    # Not a nested component array.
                    parsed_components = [{
                        'type': ComponentType.Container.value,
                        'components': list(map(
                            lambda c: c.to_json(),
                            components
                        ))
                    }]
                else:
                    # Nested component array using object Container(Component).
                    parsed_components = [c.to_json() for c in components]
            elif isinstance(components[0], (list, tuple)):
                # Nested component array using python iterables.
                parsed_components = [
                    {
                        'type': ComponentType.Container.value,
                        'components': list(map(
                            lambda c: c.to_json(),
                            children
                        ))
                    }
                    for children in components
                ]

            else:
                raise TypeError("Elements in Iterable must be Component's subclasses!")
        btn_logger.debug(
            'discord.abc.Messageable.send#patched > Parsed buttons into components : {}'.format(parsed_components))

    if file is not None and files is not None:
        raise InvalidArgument('cannot pass both file and files parameter to send()')

    if file is not None:
        if not isinstance(file, File):
            raise InvalidArgument('file parameter must be File')

        try:
            data = await state.http.send_files(channel.id, files=[file], allowed_mentions=allowed_mentions,
                                               content=content, tts=tts, embed=embed, nonce=nonce,
                                               message_reference=reference, components=parsed_components)
        finally:
            file.close()

    elif files is not None:
        if len(files) > 10:
            raise InvalidArgument('files parameter must be a list of up to 10 elements')
        elif not all(isinstance(file, File) for file in files):
            raise InvalidArgument('files parameter must be a list of File')

        try:
            data = await state.http.send_files(channel.id, files=files, content=content, tts=tts,
                                               embed=embed, nonce=nonce, allowed_mentions=allowed_mentions,
                                               message_reference=reference, components=parsed_components)
        finally:
            for f in files:
                f.close()
    else:
        data = await state.http.send_message(channel.id, content, tts=tts, embed=embed,
                                             nonce=nonce, allowed_mentions=allowed_mentions,
                                             message_reference=reference, components=parsed_components)

    ret = state.create_message(channel=channel, data=data)
    if delete_after is not None:
        await ret.delete(delay=delete_after)

    print('patched send debug : packing with ButtonMessage object...')
    print(json.dumps(data, ensure_ascii=False, indent=2))
    if 'message_reference' in data:
        # Issue : 'message_reference' object in message response data lacks 'channel_id', so copy it from object 'referenced_message'.
        data['message_reference']['channel_id'] = data['referenced_message']['channel_id']

    btn_msg: ComponentMessage = ComponentMessage.fromMessage(ret, data)
    return btn_msg


# 'send_message' method in 'discord.http.HTTPClient'
def send_message(
        self,
        channel_id,
        content,
        *,
        tts=False,
        embed=None,
        nonce=None,
        allowed_mentions=None,
        message_reference=None,
        components=None
):
    r = Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
    payload = {}

    if content:
        payload['content'] = content

    if tts:
        payload['tts'] = True

    if embed:
        payload['embed'] = embed

    if nonce:
        payload['nonce'] = nonce

    if allowed_mentions:
        payload['allowed_mentions'] = allowed_mentions

    if message_reference:
        payload['message_reference'] = message_reference

    if components:
        r"""
{
  "content": "buttons!",
  "components": [
    {
      "type": 1,
      "components": [
        {
          "type": 2,
          "style": 1,
          "custom_id": "test",
          "label": "Blurple Button"
        },
        {
          "type": 2,
          "style": 2,
          "custom_id": "test",
          "label": "Gray Button"
        },
        {
          "type": 2,
          "style": 3,
          "custom_id": "test",
          "label": "Green Button"
        },
        {
          "type": 2,
          "style": 4,
          "custom_id": "test",
          "label": "Red Button"
        },
        {
          "type": 2,
          "style": 5,
          "url": "https://google.com",
          "label": "Link Button"
        }
      ]
    }
  ]
}
        """
        btn_logger.debug('components : {}'.format(components))
        payload['components'] = components
        btn_logger.debug('payload : {}'.format(json.dumps(payload, ensure_ascii=False, indent=2)))

    return self.request(r, json=payload)


# 'send_files' method in 'discord.http.HTTPClient'
def send_files(
        self,
        channel_id,
        *,
        files,
        content=None,
        tts=False,
        embed=None,
        nonce=None,
        allowed_mentions=None,
        message_reference=None,
        components=None
):
    r = Route('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
    form = []

    payload = {'tts': tts}
    if content:
        payload['content'] = content
    if embed:
        payload['embed'] = embed
    if nonce:
        payload['nonce'] = nonce
    if allowed_mentions:
        payload['allowed_mentions'] = allowed_mentions
    if message_reference:
        payload['message_reference'] = message_reference
    if components:
        payload['components'] = components

    form.append({'name': 'payload_json', 'value': utils.to_json(payload)})
    if len(files) == 1:
        file = files[0]
        form.append({
            'name': 'file',
            'value': file.fp,
            'filename': file.filename,
            'content_type': 'application/octet-stream'
        })
    else:
        for index, file in enumerate(files):
            form.append({
                'name': 'file%s' % index,
                'value': file.fp,
                'filename': file.filename,
                'content_type': 'application/octet-stream'
            })

    return self.request(r, form=form, files=files)


def patch_dpy():
    """Replace 'send' method in 'discord.abc.Messageable' to support discord buttons feature."""
    Messageable.send = send
    HTTPClient.send_message = send_message
    HTTPClient.send_files = send_files
    Route.BASE = 'https://discord.com/api/v8'


def check():
    print('Is Messageable.send is patched? : {}'.format(Messageable.send is send))
    print('Is HTTPClient.send_message is patched? : {}'.format(HTTPClient.send_message is send_message))
    print('Is HTTPClient.send_files is patched? : {}'.format(HTTPClient.send_files is send_files))
