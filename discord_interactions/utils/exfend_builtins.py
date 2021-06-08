from typing import Any, Iterable, Optional, Union
from discord_interactions.utils.type_hints import AnyConsumer, AnyFunction


class Compute(map):
    """Similar to built-in map class, but Compute does not returns value. Instead, it runs given function with iterables."""
    def __init__(self, func: Union[AnyConsumer, AnyFunction], *iters: Iterable) -> None:
        super(Compute, self).__init__(func, *iters)

    def run(self) -> None:
        """Run function with iterables"""
        return tuple(self)


# Safe-version
class Filter(filter):
    """Extended class of built-in filter class."""
    # TODO : Study built-in map implementation and find way to access internal items without using tuple()

    @property
    def count(self) -> int:
        """Count of items in filter."""
        return len(tuple(self))

    def findFirst(self) -> Optional[Any]:
        try:
            return tuple(self)[0]
        except IndexError:
            return None

    def compute(self, func: AnyConsumer) -> None:
        Compute(func, self).run()
