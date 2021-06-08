from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Dict, Optional

from .type_hints import JSON

__all__ = (
    'JsonObject',
    'SingletonMeta'
)


class JsonObject(metaclass=ABCMeta):
    """Abstract Base Class for Json-convertible python objects"""

    @abstractmethod
    def toJson(self) -> JSON:
        """Parse object into json

        Returns:
            Parse self into dictionary object in json format.
        """
        pass

    @classmethod
    @abstractmethod
    def fromJson(cls, data: JSON) -> JsonObject:
        """Parse json data into JsonObject

        Args:
            data (JSON): dictionary object containing json data.

        Returns:
            Parsed json object.
        """
        pass


class SingletonMeta(type):
    __instances__: Dict[type, object] = {}

    def __call__(cls, *args, **kwargs) -> object:
        # print(f'Called __call__({cls}, {args}, {kwargs})') # DEBUG
        if cls not in cls.__instances__:
            instance = cls.__instances__[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
            return instance
        return cls.__instances__[cls]

    @classmethod
    def get_instance(mcs, cls: type) -> Optional[object]:
        return mcs.__instances__.get(cls)
