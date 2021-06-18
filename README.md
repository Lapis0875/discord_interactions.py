# discord_interactions.py
Wrapper library of Discord's new Interactions API, a.k.a. 'Slash Commands' feature.
Supported APIs:
1. application commands (slash commands)
2. components - Buttons

## ⚠ Warning
This repository is currently on development. I can't ensure this module works without any problems.
Since I'm preparing college entry exam, I can't keep my eyes on this project. I will read issues, but I can't say they will be resloved soon.
Every PRs are welcomed, as you keep the code's consistency (code style, docstring formats, etc.) :D

- You can use application command feature (a.k.a slash commands) in [this module](https://github.com/discord-py-slash-commands/discord-py-slash-command), too.
- You can use message components feature in [this module](https://github.com/kiki7000/discord.py-components), too.

## How to install
1. Install library from pypi
```shell
pip install discord_interactions
```
2. Import library in your project
```python
import discord_interactions
```

## Usage
### Application Commands
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

### Message Components
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
from discord_interactions.ui import SelectOption, SelectMenu
from discord.ext.commands import Bot, Context

bot = Bot(command_prefix='!')

@bot.command(
  name='select_menu'
)
async def select_cmd(ctx: Context):
    await ctx.send(components=[
      SelectMenu(
        options=[
          SelectOption(label='pizza', value=1),
          SelectOption(label='chicken', value=2)
        ],
        placeholder='Choose your favorite food'
      )
    ])
```

## Extensions
discord_interactions.ext module contains additional features of utilizing discord_interactions.

### Preset Components
**Preset Components** is a feature of parsing XML-structured Message Components into discord_interactions's python models.
(Currently in `discord_interactions.ui`. Will be moved into `discord_interactions.ext.preset_components` in future release.)

> `preset_components.xml`
```xml
<Components>
    <!-- button component structure-->
    <Button name='repository_url' style='Link' url='https://github.com/Lapis0875/discord_interactions.py' label='Repository Link' emoji='🔗'/>
    <!-- select component structure -->
    <SelectMenu name="food_poll" custom_id="food_poll" placeholder="Choose your favorite food!">
        <SelectOption label="Pizza" value="food.instant.pizza" description="Pizza is one of most popular instant food over the world." emoji = "🍕"/>
        <SelectOption label="Chicken" value="food.instant.chicken" description="CHICKEN IS THE GOD!!!" emoji="🍗"/>
        <SelectOption label="Ramen" value="food.ramen" description="Ramen is a sort of noodle dish." emoji="🍜"/>
    </SelectMenu>
    <!-- reference component object defined before. Will be replaced into matching component(based on reference name) on runtime. -->
    <ActionRow name='food_poll_view'>
    <Select ref='food_poll'/>
    </ActionRow>
</Components>
```

> `code.py`
```python
from discord_interactions.ui import SelectOption, SelectMenu, Button, Presets
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
    await ctx.send(components=[Presets.get_action_row('food_poll_view')])
```

### Object-Command Mapping (Currently, this is just a idea.)
Object-Command Mapping is a extension to implement ApplicatiomCommand objects using Class definition.
You can add Command attributes like Options, etc.
(Will be implemented in `discord_interactions.ext.ocm`)
```py
from discord_interactions.commands import Command, Option, SubCommand, SubCommandGrouo
from discord_interactions import SlashContext

class SampleSlash(Command):
    opt1 = Option(type=str)
    opt2 = Option(type=int)
    
    async def callback(self, ctx: SlashContext, opt1: str, opt2: int):
        pass 
```
```py
from discord_interactions.commands import Command, Option, SubCommand, SubCommandGrouo
from discord_interactions import SlashContext

class SubcommandaSlash(Command):
    sub = SubCommandGroup(..)
    
    @sub.subcommand
    class Msg2Ch(SubCommand):
       ch = Option(type=OptionType.Channe, ...)
        msg = Option(type=OptionType.String, ...)
        async def run(self, ctx: SlashContext, ch: discord.TextChannel, msg: str):
            await ch.sebd(msg)
    
    @sub.subcommand
    class Mention2Ch(Subcommand):
        ch = Option(OptionType.Channel, ...)
            async def callback(self, ctx: SlashContext, ch: discord.TextChannel):
                await ch.send(ctx.author.mention) 
```


## Contribute
This project follows [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/).
