from typing import List, Dict
import pandas as pd

from .minio_column import MinioColumn
from .minio_utils import correct_file_ending
from ..base_column import BaseColumn
from ..base_db import BaseDB
from ..base_table import BaseTable
from ...utils.utils import is_date, get_encoding, get_delimiter


class MinioTable(BaseTable, BaseDB):

    def __init__(self, table_path: str, table_name: str, db_name: str):
        self.__table_path = table_path
        self.__table_name = table_name
        self.__db_name = db_name
        self.__columns = dict()
        self.__get_columns_from_local_minio_tmp_copy()

    @property
    def unique_identifier(self) -> object:
        return correct_file_ending(self.__table_path)

    @property
    def db_belongs_uid(self) -> object:
        return self.__db_name

    @property
    def name(self):
        return correct_file_ending(self.__table_name)

    def get_columns(self) -> List[BaseColumn]:
        return list(self.__columns.values())

    def get_tables(self) -> Dict[str, BaseTable]:
        return {self.name: self}

    def remove_table(self, guid: object) -> BaseTable:
        pass

    def add_table(self, table: BaseTable) -> None:
        pass

    def __get_columns_from_local_minio_tmp_copy(self):
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
                self.__columns[column_name] = MinioColumn(column_name, data, d_type, str(self.unique_identifier))
            else:
                if d_type == "object":
                    self.__columns[column_name] = MinioColumn(column_name, data, "varchar", str(self.unique_identifier))
                else:
                    self.__columns[column_name] = MinioColumn(column_name, data, d_type, str(self.unique_identifier))
