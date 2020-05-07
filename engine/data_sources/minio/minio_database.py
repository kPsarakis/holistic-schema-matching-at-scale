from typing import Dict

from ..base_db import BaseDB
from ..base_table import BaseTable


class MinioDatabase(BaseDB):

    def __init__(self, db_name: str):
        self.__db_name = db_name

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
        table_to_be_removed = self.__tables[guid]
        del self.__tables[guid]
        return table_to_be_removed

    def add_table(self, table: BaseTable) -> None:
        self.__tables[table.unique_identifier] = table

    def __get_tables_from_minio(self):
        pass  # FIXME
