from typing import Union, Dict, Callable, Coroutine, Any, Literal
from discord import PartialEmoji, Emoji

__all__ = (
    'JSON',
    'YAML',
    'AnyFunction',
    'AnyConsumer',
    'CoroutineFunction',
    'Class',
    'REST_METHOD', 'RestMethod',
    'FileMode',
    'EMOJI',
)

JSON = YAML = Dict[str, Union[str, int, float, bool, dict, list]]

AnyFunction = Callable[..., Any]
AnyConsumer = Callable[..., None]

CoroutineFunction = Callable[..., Coroutine[Any, Any, Any]]
Class = type    # Class is an instance of metaclass, type.

RestMethod = REST_METHOD = Literal['GET', 'POST', 'PATCH', 'DELETE']
FileMode = Literal[
    'w', 'wt', 'wb', 'w+', 'w+t', 'w+b',
    'r', 'rt', 'rb', 'r+', 'r+t', 'r+b',
    'a', 'at', 'ab', 'a+', 'a+t', 'a+b',
    'x', 'xt', 'xb', 'x+', 'x+t', 'x+b',
]

EMOJI = Union[Emoji, PartialEmoji, str]
