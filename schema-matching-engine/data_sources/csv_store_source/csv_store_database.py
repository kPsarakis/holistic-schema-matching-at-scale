import os
from typing import Dict

from data_sources.base_db import BaseDB
from data_sources.base_table import BaseTable
from data_sources.csv_store_source.csv_store_table import CSVStoreTable


class CSVStoreDatabase(BaseDB):

    def __init__(self, db_path: str, db_name: str):
        self.__db_name = db_name
        self.__db_path = db_path

        self.__tables: Dict[object, BaseTable] = dict()
        self.__get_tables_from_csv_store()

    @property
    def unique_identifier(self) -> object:
        return self.__db_path

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

    def __get_tables_from_csv_store(self):
        for root, dirs, files in os.walk(os.path.join(self.__db_path)):
            for file in files:
                table_path: str = root + os.path.sep + file
                table_name: str = table_path.split(os.path.sep)[-1].split(".")[0]
                self.__tables[table_name] = CSVStoreTable(table_path, table_name, self.__db_name)
