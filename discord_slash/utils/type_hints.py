from typing import Union, Dict, Callable, Coroutine, Any

__all__ = (
    'JSON',
    'YAML',
    'Function',
    'CoroutineFunction',
    'Class'
)

JSON = YAML = Dict[str, Union[str, int, float, bool, dict, list]]
Function = Callable[..., Any]
CoroutineFunction = Callable[..., Coroutine[...]]
Class = type    # Class is an instance of metaclass, type.
