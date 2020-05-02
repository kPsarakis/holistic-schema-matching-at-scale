from abc import ABC, abstractmethod
from typing import Dict, Union

from data_sources.base_db import BaseDB
from data_sources.base_table import BaseTable


class BaseSource(ABC):
    """
    Abstract class representing a source (i.e. Atlas, csv_file_store)
    """

    @abstractmethod
    def get_db(self, guid: object) -> BaseDB:
        raise NotImplementedError

    @abstractmethod
    def get_all_dbs(self) -> Dict[object, BaseDB]:
        raise NotImplementedError

    @abstractmethod
    def get_db_table(self, guid: object, db_guid: object = None) -> Union[BaseDB, BaseTable]:
        raise NotImplementedError
