"""
Wrapper of discord interactions api.
"""
import application_commands
import ui
from .utils.log import get_stream_logger, DEBUG

slash_logger = get_stream_logger('discord_interactions', DEBUG)
