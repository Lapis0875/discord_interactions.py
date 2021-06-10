"""
discord_interactions.client
~~~~~~
client class for slash-command usage.
"""

from .application_command_client import SlashClient, AutoShardedSlashClient, SlashBot, AutoShardedSlashBot
# Future : http-only client implementation. (only use application command oauth2 scope)
