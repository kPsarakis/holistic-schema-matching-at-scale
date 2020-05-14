import os
from typing import Dict
from minio import Minio

from .minio_table import MinioTable
from .minio_utils import correct_file_ending
from ..base_db import BaseDB
from ..base_table import BaseTable
from ...utils.utils import create_folder, get_project_root


class MinioDatabase(BaseDB):

    def __init__(self, minio_client: Minio, db_name: str):
        self.__minio_client: Minio = minio_client
        self.__db_name: str = db_name

        self.__tables: Dict[object, BaseTable] = dict()
        self.__get_tables_from_minio()

    @property
    def unique_identifier(self) -> object:
        return self.__db_name

    @property
    def name(self) -> str:
        return self.__db_name

    def get_tables(self) -> Dict[str, BaseTable]:
        tables: Dict[str, BaseTable] = {val.name: val for val in self.__tables.values() if val.number_of_columns > 0}
        return tables

    def remove_table(self, guid: object) -> BaseTable:
        guid = correct_file_ending(str(guid))
        table_to_be_removed = self.__tables[guid]
        del self.__tables[guid]
        return table_to_be_removed

    def add_table(self, table: BaseTable) -> None:
        self.__tables[table.unique_identifier] = table

    def __get_tables_from_minio(self):
        local_tmp_minio_path = get_project_root() + '/tmp_minio_folder'
        create_folder(local_tmp_minio_path)
        objects = self.__minio_client.list_objects(self.__db_name, prefix=None, recursive=True)
        for obj in objects:
            table_path: str = local_tmp_minio_path + '/' + obj.object_name
            self.__minio_client.fget_object(self.__db_name, obj.object_name, table_path)
            table_name: str = obj.object_name.split("/")[-1]
            self.__tables[table_name] = MinioTable(table_path, table_name, self.__db_name)
            os.remove(table_path)
