from typing import List, Dict

from ..base_column import BaseColumn
from ..base_db import BaseDB
from ..base_table import BaseTable


class MinioTable(BaseTable, BaseDB):

    def __init__(self, table_path: str, table_name: str, db_name: str):
        self.__table_path = table_path
        self.__table_name = table_name
        self.__db_name = db_name
        self.__columns = dict()
        self.__get_columns_from_local_minio_cache()

    @property
    def unique_identifier(self) -> object:
        return self.__table_path

    @property
    def db_belongs_uid(self) -> object:
        return self.__db_name

    @property
    def name(self):
        return self.__table_name

    def get_columns(self) -> List[BaseColumn]:
        return list(self.__columns.values())

    def get_tables(self) -> Dict[str, BaseTable]:
        return {self.name: self}

    def remove_table(self, guid: object) -> BaseTable:
        pass

    def add_table(self, table: BaseTable) -> None:
        pass

    def __get_columns_from_local_minio_cache(self):
        pass  # FIXME
