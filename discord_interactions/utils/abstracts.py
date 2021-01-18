from __future__ import annotations
from abc import ABCMeta, abstractmethod
from .type_hints import JSON


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
