# discord_interactions.py
Wrapper library of Discord's new Interactions API, a.k.a. 'Slash Commands' feature.
Supported APIs:
1. application commands (slash commands)
2. components - Buttons

## ⚠ Warning
This repository is currently on development. I can't ensure this module works without any problems.
Since I'm preparing college entry exam, I can't keep my eyes on this project. I will read issues, but I can't say they will be resloved soon.
Every PRs are welcomed, as you keep the code's consistency (code style, docstring formats, etc.) :D

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

> `preset_components.xml`
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

"""
discord_interactions.ui.Presets is a singleton class, which parse and stores xml-structured message components.
You can get those preset components through methods like:
  ActionRow : Presets().get_action_row(name)
  Button : Presets().get_button(name)
  Select : Presets().get_select(name)
  SelectOption : Presets().get_select_option(name)
Parameter `name` is defined in xml component tags as a attribute 'name`.
You can get these preset components using `name` attribute value.
"""
Presets().load_xml('preset_components.xml')

@bot.command(name='repository')
async def repo_btn_cmd(ctx: Context):
    await ctx.send(components=[Presets.get_button('repository_url')])

@bot.command(name='food_poll')
async def fool_poll_cmd(ctx: Context):
    await ctx.send(components=Presets.get_action_row('food_poll_view'))
```

## Contribute
This project follows [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/).
