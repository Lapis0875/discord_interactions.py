"""
Wrapper of discord interactions api.
"""
from .utils.log import get_stream_logger, DEBUG
from .utils.abstracts import SingletonMeta, JsonObject
from .utils.type_hints import JSON, EMOJI, FileMode, Class, RestMethod
from .utils.interaction_route import InteractionRoute
from .application_commands.client import SlashClient, SlashBot, AutoShardedSlashClient, AutoShardedSlashBot
from .application_commands.models import *
from .ui import Component, ComponentType, ActionRow, Button, ButtonStyle

slash_logger = get_stream_logger('discord_interactions', DEBUG)
