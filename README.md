# discord_interactions.py
Wrapper library of Discord's new Interactions API, a.k.a. 'Slash Commands' feature.
Supported APIs:
1. application commands (slash commands)
2. components - Buttons

## How to install
1. Install library from pypi
```shell
pip install discord_interactions
```
2. Import library in your project
```python
import discord_interactions
```

## How to use - Application Commands
> discord.ext.commands.Bot + `Application Commands`

```python
from discord_interactions.application_commands import Bot, SlashContext

bot = Bot(command_prefix='!')

@bot.application_command(
  name='hello'
)
async def hello_slash(ctx: SlashContext):
    await ctx.respond() # WIP
```

## How to use - Message Components
> Buttons
```python
from discord_interactions.ui import ButtonStyle, Button
from discord.ext.commands import Bot, Context

bot = Bot(command_prefix='!')

@bot.command(
  name='buttons'
)
async def btn_cmd(ctx: Context):
    await ctx.send(components=[Button(style=ButtonStyle.Success, label='I'm Green!', custom_id='btn01', emoji='📗')])
```

> Select Menu
```python
from discord_interactions.ui import SelectOption, Select
from discord.ext.commands import Bot, Context

bot = Bot(command_prefix='!')

@bot.command(
  name='select_menu'
)
async def select_cmd(ctx: Context):
    await ctx.send(components=[
      Select(
        options=[
          SelectOption(label='pizza', value=1),
          SelectOption(label='chicken', value=2)
        ],
        placeholder='Choose your favorite food'
      )
    ])
```

## How to use - XML Message Components (Experimental)

> `preset_buttons.xml`
```xml
<Components>
  <!-- button component structure-->
  <Button name='repository_url' style='Link' url='https://github.com/Lapis0875/discord_interactions.py' label='Repository Link' emoji='🔗'/>
  <!-- select component structure -->
  <Select name='food_poll' placeholder='Choose your favorite food'>
    <SelectOption label='pizza' value='1'/>
    <SelectOption label='chicken' value='2'/>
  </Select>
  <!-- reference component object defined before. Will be replaced into matching component(based on reference name) on runtime. -->
  <ActionRow name='food_poll_view'>
    <Select ref='food_poll'/>
  </ActionRow>
</Components>
```
> `code.py`
```python
from discord_interactions.ui import SelectOption, Select, Button, Presets
from discord.ext.commands import Bot, Context

bot = Bot(command_prefix='!')

@bot.command(name='repository')
async def repo_btn_cmd(ctx: Context):
    await ctx.send(components=[Presets.get_button('repository_url')])

@bot.command(name='food_poll')
async def fool_poll_cmd(ctx: Context):
    await ctx.send(components=Presets.get_action_row('food_poll_view'))
```

## Contribute
This project follows [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/).
