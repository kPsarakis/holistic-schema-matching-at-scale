from abc import ABC, abstractmethod

from typing import Dict

from data_sources.base_table import BaseTable


class BaseDB(ABC):
    """
    Abstract class representing a database
    """

    @property
    @abstractmethod
    def unique_identifier(self) -> object:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_tables(self) -> Dict[str, BaseTable]:
        raise NotImplementedError

    @abstractmethod
    def remove_table(self, guid: object) -> BaseTable:
        raise NotImplementedError

    @abstractmethod
    def add_table(self, table: BaseTable) -> None:
        raise NotImplementedError

    @property
    def number_of_tables(self) -> int:
        return len(self.get_tables())

    @property
    def number_of_columns(self) -> int:
        number_of_columns = 0
        for table in self.get_tables().values():
            number_of_columns += table.number_of_columns
        return number_of_columns

    def __str__(self):
        __str = "DB: " + self.name + "  |  " + str(self.unique_identifier) + "\n"
        for table in self.get_tables().values():
            __str = __str + table.__str__()
        return __str
