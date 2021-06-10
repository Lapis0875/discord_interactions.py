from pprint import pprint

from discord_interactions.ui.xml_preset import Presets
from discord_interactions.ui.components import ActionRow, Button, SelectMenu, SelectOption

Presets().load_xml('../resources/ui/sample_buttons.xml')
Presets().load_xml('../resources/ui/sample_selects.xml')
Presets().load_xml('../resources/ui/sample_action_rows.xml')

primary_btn: Button = Presets().get_button('primary_button')
poll_select: SelectMenu = Presets().get_select_menu('select_sample')
action_row_ref: ActionRow = Presets().get_action_row('button_action_row_ref')

pprint(Presets().get_components(), indent=2)

print(primary_btn)
print(poll_select)
print(action_row_ref)
