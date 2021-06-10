from discord.ext.commands import Bot, Context
from discord_interactions import ui
from discord_interactions.ui import Presets

token = 'YOUR_TOKEN'
bot = Bot(command_prefix='!')


@bot.command(
    name='components'
)
async def component_cmd(ctx: Context):
    await ctx.send(
        'Message Components Test!',
        components=[
            ui.ActionRow([
                ui.Button(style=ui.ButtonStyle.Primary, label='Primary Button', emoji='😀', disabled=False, custom_id='primary_btn'),
                ui.Button(style=ui.ButtonStyle.Secondary, label='Secondary Button', emoji='😀', disabled=False, custom_id='secondary_btn'),
                ui.Button(style=ui.ButtonStyle.Success, label='Success Button', emoji='😀', disabled=False, custom_id='success_btn'),
                ui.Button(style=ui.ButtonStyle.Danger, label='Danger Button', emoji='😀', disabled=False, custom_id='danger_btn'),
                ui.Button(style=ui.ButtonStyle.Link, label='Repository Link', emoji='😀', disabled=False, url='https://github.com/Lapis0875/discord_interactions.py')
            ]),
            ui.ActionRow([Presets().get_action_row('food_poll')])
        ]
    )


@bot.command(
    name='buttons'
)
async def button_cmd(ctx: Context):
    await ctx.send(
        'Your buttons, sir.',
        components=[
            ui.ActionRow([
                ui.Button(style=ui.ButtonStyle.Primary, label='Primary Button', emoji='😀', disabled=False, custom_id='primary_btn'),
                ui.Button(style=ui.ButtonStyle.Secondary, label='Secondary Button', emoji='😀', disabled=False, custom_id='secondary_btn'),
                ui.Button(style=ui.ButtonStyle.Success, label='Success Button', emoji='😀', disabled=False, custom_id='success_btn'),
                ui.Button(style=ui.ButtonStyle.Danger, label='Danger Button', emoji='😀', disabled=False, custom_id='danger_btn'),
                ui.Button(style=ui.ButtonStyle.Link, label='Repository Link', emoji='😀', disabled=False, url='https://github.com/Lapis0875/discord_interactions.py')
            ])
        ]
    )


@bot.command(
    name='select_menu'
)
async def select_menu_cmd(ctx: Context):
    await ctx.send(
        'Your buttons, sir.',
        components=ui.ActionRow([Presets().get_action_row('food_poll')])
    )


bot.run(token)
