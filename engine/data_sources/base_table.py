from abc import ABC, abstractmethod
from typing import List, Dict
from cached_property import cached_property

from .base_column import BaseColumn


class BaseTable(ABC):
    """
    Abstract class representing a table
    """

    @property
    @abstractmethod
    def unique_identifier(self) -> object:
        raise NotImplementedError

    @property
    @abstractmethod
    def db_belongs_uid(self) -> object:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_columns(self) -> List[BaseColumn]:
        raise NotImplementedError

    @property
    def number_of_columns(self) -> int:
        return len(self.get_columns())

    @cached_property
    def get_guid_column_lookup(self) -> Dict[str, object]:
        return {column.name:  column.unique_identifier for column in self.get_columns()}

    def __str__(self):
        __str: str = "\tTable: " + self.name + "  |  " + str(self.unique_identifier) + "\n"
        for column in self.get_columns():
            __str = __str + str(column.__str__())
        return __str
