from typing import Dict, List
from minio import Minio

from .minio_table import MinioTable
from .minio_utils import correct_file_ending
from ..base_db import BaseDB
from ..base_table import BaseTable


class MinioDatabase(BaseDB):

    def __init__(self, minio_client: Minio, db_name: str):
        self.__minio_client: Minio = minio_client
        self.__db_name: str = db_name
        self.__tables: Dict[object, BaseTable] = dict()
        self.__get_tables_from_minio(load_data=False)

    @property
    def unique_identifier(self) -> str:
        return self.__db_name

    @property
    def name(self) -> str:
        return self.__db_name

    def get_tables(self, load_data: bool = True) -> Dict[str, BaseTable]:
        self.__get_tables_from_minio(load_data)
        tables: Dict[str, BaseTable] = {val.name: val for val in self.__tables.values() if not val.is_empty}
        return tables

    def remove_table(self, guid: object) -> BaseTable:
        guid = correct_file_ending(str(guid))
        table_to_be_removed = self.__tables[guid]
        del self.__tables[guid]
        return table_to_be_removed

    def add_table(self, table: BaseTable) -> None:
        self.__tables[table.unique_identifier] = table

    def get_table_str_guids(self) -> List[tuple]:
        return list(map(lambda x: (self.__db_name, x.object_name),
                        self.__minio_client.list_objects(self.__db_name, prefix=None, recursive=True)))

    @property
    def is_empty(self) -> bool:
        return len(list(self.__minio_client.list_objects(self.__db_name, prefix=None, recursive=True))) == 0

    def __get_tables_from_minio(self, load_data: bool):
        objects = self.__minio_client.list_objects(self.__db_name, prefix=None, recursive=True)
        for obj in objects:
            self.__tables[obj.object_name] = MinioTable(self.__minio_client, obj.object_name, self.__db_name, load_data)
