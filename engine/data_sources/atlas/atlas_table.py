from typing import List

from .atlas_column import AtlasColumn
from .atlas_utils import get_bulk_entities
from ..base_db import BaseDB
from ..base_table import BaseTable


class AtlasTable(BaseTable, BaseDB):

    def __init__(self, url: str, auth: tuple, table_name: str, guid: str, column_guids: list, technology: str,
                 db_guid: str, chunk_size: int):
        self.__db_guid = db_guid
        self.__guid = guid
        self.__url = url
        self.__auth = auth
        self.__chunk_size = chunk_size * 2
        self.__table_name = table_name
        self.__column_guids = column_guids
        self.__technology = technology
        self.__columns = dict()
        self.__get_columns_from_atlas()

    @property
    def unique_identifier(self):
        return self.__guid

    @property
    def db_belongs_uid(self) -> object:
        return self.__db_guid

    @property
    def name(self):
        return self.__table_name

    def get_columns(self) -> List[AtlasColumn]:
        return list(self.__columns.values())

    def get_tables(self):
        return {self.name: self}

    def remove_table(self, guid: object) -> None:
        pass

    def add_table(self, table) -> None:
        pass

    def __get_columns_from_atlas(self):
        if len(self.__column_guids) == 0:
            return

        for i in range(len(self.__column_guids) // self.__chunk_size + 1):
            chunk: list = self.__column_guids[i * self.__chunk_size:(i + 1) * self.__chunk_size]
            if len(chunk) == 0:
                continue
            entities = get_bulk_entities(self.__url, self.__auth, chunk)['entities']
            for column in entities:
                self.__columns[column['guid']] = AtlasColumn(column['attributes']['name'],
                                                             column['attributes']['type'],
                                                             column['guid'])
