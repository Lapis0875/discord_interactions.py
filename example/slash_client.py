import asyncio

from discord import User

from discord_interactions.application_commands.client import SlashClient
from discord_interactions.application_commands.models import ApplicationCommandOption, ApplicationCommandOptionType,\
    IntegerCommandOption, UserCommandOption, StringCommandOption, BooleanCommandOption, ChannelCommandOption, RoleCommandOption, SlashContext

token = 'YOUR_TOKEN'
client = SlashClient()


@client.globalSlash(
    name='hello',
    description='Send greetings to user.',
    options=[
        ApplicationCommandOption(
            name='user',
            option_type=ApplicationCommandOptionType.USER,
            description='User to send greeting.',
            required=True,
            default=True
        ),
        ApplicationCommandOption(
            name='text',
            option_type=ApplicationCommandOptionType.STRING,
            description='Text of greeting message.',
            required=False
        )
    ]
)
async def hello(ctx: SlashContext, user: User, text: str = 'Hello {user.mention}!'):
    await ctx.send(text.format(user=user))


@hello.before_hook
async def before_hello(ctx: SlashContext):
    # TODO : What parameters do before_hooks should receive?
    print('Before calling SlashCommand "hello"')
    print(ctx.__dict__)


@hello.after_hook
async def after_hello(ctx: SlashContext, user: User, text: str):
    # TODO : What parameters do after_hooks should receive?
    print('After calling SlashCommand "hello"')
    print(ctx, user, text)


@client.globalSlash(
    name='alarm',
    description='Alarm user after given duration. Slash command sample using Annotation objects on type hints!'
)
async def alarm(
        ctx: SlashContext,
        user: UserCommandOption(name='user', description='target user', required=True, default=False),
        duration: IntegerCommandOption(name='duration', description='duration until alarm rings', required=True, default=False),
        text: StringCommandOption(name='text', description='alarm text', required=False, default=False) = 'Alarm done! {user.mention}'
):
    await asyncio.sleep(duration)
    await user.dm_channel.send(text.format(user=user))


@client.globalSlash(
    name='sample',
    description='sample command using type annotations to register command options'
)
async def sampleSlashCommand(
        ctx: SlashContext,

        integer: IntegerCommandOption(name='IntegerArg', description='Integer Command Option Type Hint Test',
                                      required=True, default=False),
        string: StringCommandOption(name='StringArg', description='String Command Option Type Hint Test',
                                    required=False, default=False),
        boolean: BooleanCommandOption(name='BooleanArg', description='Boolean Command Option Type Hint Test',
                                      required=False, default=True),
        user: UserCommandOption(name='UserArg', description='discord.User Command Option Type Hint Test',
                                required=False, default=False),
        channel: ChannelCommandOption(name='ChannelArg',
                                      description='discord.abc.GuildChannel Command Option Type Hint Test',
                                      required=False, default=False),
        role: RoleCommandOption(name='RoleArg', description='discord.Role Command Option Type Hint Test',
                                required=False, default=False)
):
    print(integer)
    print(string)
    print(boolean)
    print(user)
    print(channel)
    print(role)


print(type(alarm))
# client.run(token)
