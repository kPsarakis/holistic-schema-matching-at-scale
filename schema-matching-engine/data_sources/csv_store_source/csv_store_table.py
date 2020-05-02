import pandas as pd
from typing import List

from data_sources.base_db import BaseDB
from data_sources.base_table import BaseTable
from data_sources.csv_store_source.csv_store_column import CSVStoreColumn
from utils.utils import get_encoding, get_delimiter, is_date


class CSVStoreTable(BaseTable, BaseDB):

    def __init__(self, table_path: str, table_name: str, db_name: str):
        self.__table_path = table_path
        self.__table_name = table_name
        self.__db_name = db_name
        self.__columns = dict()
        self.__get_columns_from_csv_store()

    @property
    def unique_identifier(self) -> object:
        return self.__table_path

    @property
    def db_belongs_uid(self) -> object:
        return self.__db_name

    @property
    def name(self):
        return self.__table_name

    def get_columns(self) -> List[CSVStoreColumn]:
        return list(self.__columns.values())

    def get_tables(self):
        return {self.name: self}

    def remove_table(self, guid: object) -> None:
        pass

    def add_table(self, table) -> None:
        pass

    def __get_columns_from_csv_store(self):
        table_df: pd.DataFrame = pd.read_csv(self.__table_path,
                                             index_col=False,
                                             encoding=get_encoding(self.__table_path),
                                             sep=get_delimiter(self.__table_path),
                                             error_bad_lines=False).fillna('')
        for (column_name, column_data) in table_df.iteritems():
            d_type = str(column_data.dtype)
            data = list(filter(lambda d: d != '', list(column_data.values)))  # remove the NaN values
            if len(data) != 0:
                if d_type == "object":
                    if is_date(data[0]):
                        d_type = "date"
                    else:
                        d_type = "varchar"
                self.__columns[column_name] = CSVStoreColumn(column_name, data, d_type)
            else:
                if d_type == "object":
                    self.__columns[column_name] = CSVStoreColumn(column_name, data, "varchar")
                else:
                    self.__columns[column_name] = CSVStoreColumn(column_name, data, d_type)
