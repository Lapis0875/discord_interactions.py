from __future__ import annotations
from abc import ABCMeta, abstractmethod
from .type_hints import JSON


class JsonObject(metaclass=ABCMeta):

    @abstractmethod
    def toJson(cls) -> JSON:
        """

        """
        ...

    @classmethod
    @abstractmethod
    def fromJson(cls, data: JSON) -> JsonObject:
        """Parse json data into JsonObject

        :param data:
        :return:
        """
        ...
