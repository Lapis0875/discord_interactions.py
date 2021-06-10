from enum import Enum
from typing import Final, List, Dict, Optional, Tuple
from xml.etree.ElementTree import parse, ElementTree, Element

from discord import PartialEmoji

from discord_interactions.utils.type_hints import JSON, EMOJI
from discord_interactions.utils.abstracts import SingletonMeta
from .errors import DiscordUIError
from .components import Component, ActionRow, Button, ButtonStyle, ButtonKeys, SelectOption, SelectMenu, SelectOptionKeys, SelectKeys

# Tag Names
# - structure tag
COMPONENTS: Final[str] = 'Components'
EMOJI_TAG: Final[str] = 'Emoji'
# - meta tag
NAME: Final[str] = 'name'
REFERENCE: Final[str] = 'ref'
# - component tag
ACTION_ROW: Final[str] = ActionRow.__name__
BUTTON: Final[str] = Button.__name__
SELECT_OPTION: Final[str] = SelectOption.__name__
SELECT_MENU: Final[str] = SelectMenu.__name__


__all__ = (
    'Presets',
    'XMLComponentParser'
)


class EmojiKeys:
    NAME = 'name'
    ANIMATED: Final[str] = 'animated'
    ID: Final[str] = 'id'


class PostponedKeys:
    PARENT: Final[str] = 'parent'
    CONTAINER: Final[str] = 'container'
    REFERENCE_NAME: Final[str] = 'reference'
    CLASS: Final[str] = 'class'


"""
xml component parsers
"""


class ComponentParseError(DiscordUIError):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return self.__str__()


class InvalidComponentReference(ComponentParseError):
    def __init__(self, parent: Component, reference: str):
        super(InvalidComponentReference, self).__init__(
            'Reference `{}` used in parent component {!r} is not found!'.format(reference, parent)
        )
        self.reference = reference


class InvalidComponentStructure(ComponentParseError):
    def __init__(self, component_type: str):
        super(InvalidComponentStructure, self).__init__(
            'Component type {} has malformed structure.'.format(component_type)
        )


def _parse_boolean(value: str) -> bool:
    if value in ('false', 'False', 'FALSE'):
        return False
    elif value in ('true', 'True', 'TRUE'):
        return True
    else:
        raise ValueError('discord_interactions.ui.xml_preset failed parse boolean value in tag attribute : '
                         'expected value of either true or false, not {}'.format(value))


def _parse_emoji(component_tag: Element) -> Optional[EMOJI]:
    # Search for partial emoji attribute
    emoji = component_tag.get(ButtonKeys.EMOJI)
    if emoji is None:
        # Search for inner Emoji tag
        emoji_tag = component_tag.find(EMOJI_TAG)
        if emoji_tag is None:
            return None

        animated_raw: str = emoji_tag.get(EmojiKeys.ANIMATED)
        animated: bool = animated_raw and _parse_boolean(animated_raw)
        return PartialEmoji(
            name=emoji_tag.get(EmojiKeys.NAME),
            animated=animated,
            id=int(emoji_tag.get(EmojiKeys.ID))
        )


class XMLComponentParser:
    def __init__(self, storage: Optional[Dict] = None):
        self.parsed: Dict[str, Dict[str, Component]] = storage or {
            ACTION_ROW: {},
            BUTTON: {},
            SELECT_MENU: {},
            SELECT_OPTION: {}
        }
        self.postponed_queue: List[JSON] = []

    def _parse_button_from_tag(
            self,
            button_tag: Element,
            *,
            parent: Optional[ActionRow]
    ) -> Tuple[Optional[Button], Optional[str]]:
        # reference tag checks.
        # Example : <Button ref="some_ref_name"/>
        ref = button_tag.get(REFERENCE)
        if ref:
            # Postpone to parse after primary parsing.
            self.postponed_queue.append(
                {
                    PostponedKeys.PARENT: parent,
                    PostponedKeys.REFERENCE_NAME: ref,
                    PostponedKeys.CLASS: Button
                }
            )
            return None, ref

        style_raw: str = button_tag.attrib[ButtonKeys.STYLE]
        style_to_parse = int(style_raw) if style_raw.isdigit() else style_raw

        disabled_raw: str = button_tag.get(ButtonKeys.DISABLED)
        disabled = disabled_raw and _parse_boolean(disabled_raw)

        return Button(
            # Required
            style=ButtonStyle.parse(style_to_parse),
            # Optional
            label=button_tag.get(ButtonKeys.LABEL),
            emoji=_parse_emoji(button_tag),
            disabled=disabled,
            url=button_tag.get(ButtonKeys.URL),
            custom_id=button_tag.get(ButtonKeys.CUSTOM_ID)
        ), button_tag.get(NAME)

    def _parse_select_option_from_tag(
            self,
            option_tag: Element,
            *,
            parent: Optional[SelectMenu] = None,
            container: Optional[list] = None
    ) -> Tuple[Optional[SelectOption], Optional[str]]:
        # reference tag checks.
        # Example : <SelectOption ref="some_ref_name"/>
        ref = option_tag.get(REFERENCE)
        if ref:
            print(f'Adding reference for SelectOption with name {ref}')
            # Postpone to parse after primary parsing.
            self.postponed_queue.append(
                {
                    PostponedKeys.PARENT: parent,
                    PostponedKeys.CONTAINER: container,
                    PostponedKeys.REFERENCE_NAME: ref,
                    PostponedKeys.CLASS: SelectOption
                }
            )
            return None, ref

        default_raw: str = option_tag.get(SelectOptionKeys.DEFAULT)
        default: bool = default_raw and _parse_boolean(default_raw)

        return SelectOption(
            # Required
            label=option_tag.attrib[SelectOptionKeys.LABEL],
            value=option_tag.attrib[SelectOptionKeys.VALUE],
            # Optional
            emoji=_parse_emoji(option_tag),
            description=option_tag.get(SelectOptionKeys.DESCRIPTION),
            default=default
        ), option_tag.get(NAME)

    def parse_select_options(self, select_tag: Element) -> List[SelectOption]:
        options: List[SelectOption] = []
        for option in select_tag.iter(SELECT_OPTION):
            option, _ = self._parse_select_option_from_tag(option, container=options)
            if option:
                options.append(option)

        return options

    def _parse_select_menu_from_tag(
            self,
            select_tag: Element,
            *,
            parent: Optional[ActionRow]
    ) -> Tuple[Optional[SelectMenu], Optional[str]]:
        # reference tag checks.
        # Example : <Select ref="some_ref_name"/>
        ref = select_tag.get(REFERENCE)
        if ref:
            # Postpone to parse after primary parsing.
            self.postponed_queue.append(
                {
                    PostponedKeys.PARENT: parent,
                    PostponedKeys.REFERENCE_NAME: ref,
                    PostponedKeys.CLASS: SelectMenu
                }
            )
            return None, ref

        options: List[SelectOption] = self.parse_select_options(select_tag)

        return SelectMenu(
            # Required
            options=options,
            # Optional
            custom_id=select_tag.get(SelectKeys.CUSTOM_ID),
            placeholder=select_tag.get(SelectKeys.PLACEHOLDER),
            min_values=select_tag.get(SelectKeys.MIN_VALUES),
            max_values=select_tag.get(SelectKeys.MAX_VALUES)
        ), select_tag.get(NAME)

    def load_xml_action_rows(self, root: Element) -> Dict[str, ActionRow]:
        action_rows: Dict[str, ActionRow] = {}

        for action_row in root.iterfind(ACTION_ROW):
            action_row_childs: List[Component] = []

            # TODO
            # Experimental : list is passed through pointer,
            # so intensionally modify list after object creation.
            action_row_obj = action_rows[action_row.attrib[NAME]] = ActionRow(child_components=action_row_childs)

            # One ActionRow can only contain either list of buttons or a select.
            # Search buttons first.
            buttons: List[Element] = action_row.findall(BUTTON)
            if len(buttons) > 0:
                # In this case, parse only button components.
                for button_tag in buttons:
                    button, _ = self._parse_button_from_tag(button_tag, parent=action_row_obj)
                    if button is not None:
                        action_row_obj.add_child(button)

                continue

            # Search select menus next.
            selects: List[Element] = action_row.findall(SELECT_MENU)
            if len(selects) > 0:
                # In this case, parse only select menu components.
                for select in selects:
                    # TODO
                    # Experimental : list is passed through pointer,
                    # so intensionally modify list after object creation.
                    select_obj, _ = self._parse_select_menu_from_tag(select, parent=action_row_obj)
                    if select_obj is not None:
                        action_row_obj.add_child(select_obj)

                continue

            # When code reaches to this line, it means this ActionRow tag does not have any valid Component tags.
            raise InvalidComponentStructure(ACTION_ROW)

        return action_rows

    def load_xml_buttons(self, root: Element) -> Dict[str, Button]:
        buttons: Dict[str, Button] = {}
        for button_tag in root.iterfind(BUTTON):
            btn, name = self._parse_button_from_tag(button_tag, parent=None)
            if btn is not None:
                buttons[name] = btn

        return buttons

    def load_xml_select_menus(self, root: Element) -> Dict[str, SelectMenu]:
        selects: Dict[str, SelectMenu] = {}
        for select_tag in root.iterfind(SELECT_MENU):
            select, name = self._parse_select_menu_from_tag(select_tag, parent=None)
            if select is not None:
                selects[name] = select

        return selects

    def load_xml_select_options(self, root: Element) -> Dict[str, SelectOption]:
        """
        Parse SelectOption tags into SelectOption objects. This function only parses SelectOption tags in root.
        No forward-reference is allowed in here, since this function parse a single SelectOption object in root.
        Why you need to use reference in a sole SelectOption tag?
        :param root:
        :return:
        """
        return {opt.attrib[NAME]: self._parse_select_option_from_tag(opt, parent=None, container=None) for opt in root.iterfind(SELECT_OPTION)}

    def load_xml_components(self, xml_file_path: str) -> Dict[str, Dict[str, Component]]:
        tree: ElementTree = parse(xml_file_path)
        component_root: Element = tree.getroot()

        try:
            action_rows = self.load_xml_action_rows(component_root)
        except InvalidComponentStructure:
            # This xml does not contain ActionRow.
            action_rows = {}

        try:
            buttons = self.load_xml_buttons(component_root)
        except InvalidComponentStructure:
            # This xml does not contain Button.
            buttons = {}

        try:
            selects = self.load_xml_select_menus(component_root)
        except InvalidComponentStructure:
            # This xml does not contain Button.
            selects = {}

        try:
            select_options = self.load_xml_select_options(component_root)
        except InvalidComponentStructure:
            # This xml does not contain Button.
            select_options = {}

        # Primary Parse
        loaded = {
            ACTION_ROW: action_rows,
            BUTTON: buttons,
            SELECT_MENU: selects,
            SELECT_OPTION: select_options
        }

        # Consume Postponed Queue
        delayed_postponed_queue: List[JSON] = []
        for context in self.postponed_queue:
            parent: Optional[Component] = context[PostponedKeys.PARENT]
            reference: str = context[PostponedKeys.REFERENCE_NAME]
            target_class: type = context[PostponedKeys.CLASS]

            # Try to find reference in the primary-parsed components. Then, search in previously parsed components (can be parsed in other files.)
            component: Optional[Component] = loaded[target_class.__name__].get(reference) or self.parsed[target_class.__name__].get(reference)
            if component is None:
                delayed_postponed_queue.append(context)
            if target_class in (Button, SelectMenu):
                parent: ActionRow
                parent.add_child(component)
            elif target_class == SelectOption:
                parent: SelectMenu
                container = context[PostponedKeys.CONTAINER]
                container.append(component)

        self.postponed_queue = delayed_postponed_queue  # can be parsed after parsing other files.

        self.parsed[ACTION_ROW].update(action_rows)
        self.parsed[BUTTON].update(buttons)
        self.parsed[SELECT_MENU].update(selects)
        self.parsed[SELECT_OPTION].update(select_options)

        return self.parsed


class Presets(metaclass=SingletonMeta):
    """
    Preset component storage.
    """
    def __init__(self):
        self.storage: Dict[str, Dict[str, Component]] = {
            ACTION_ROW: {},
            BUTTON: {},
            SELECT_MENU: {},
            SELECT_OPTION: {}
        }
        self.parser = XMLComponentParser(storage=self.storage)

    def load_xml(self, path: str) -> None:
        parsed = self.parser.load_xml_components(path)
        # since parser manually modifies dictionary(storage), we can just call the method and ignore the return.
        # self.storage.update(parsed)

    def get_components(self) -> Dict[str, Dict[str, Component]]:
        return self.storage

    def get_action_row(self, name: str) -> Optional[ACTION_ROW]:
        return self.storage[ACTION_ROW].get(name)

    def get_button(self, name: str) -> Optional[Button]:
        return self.storage[BUTTON].get(name)

    def get_select_menu(self, name: str) -> Optional[SelectMenu]:
        return self.storage[SELECT_MENU].get(name)

    def get_select_option(self, name: str) -> Optional[SelectOption]:
        return self.storage[SELECT_OPTION].get(name)
