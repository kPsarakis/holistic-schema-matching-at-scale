from ..base_column import BaseColumn


class CSVStoreColumn(BaseColumn):

    def __init__(self, column_name: str, data: list, d_type: str):
        self.__column_name = column_name
        self.__data = data
        self.__d_type = d_type

    @property
    def unique_identifier(self) -> object:
        return self.__column_name

    @property
    def name(self):
        return self.__column_name

    @property
    def data_type(self):
        return self.__d_type

    @property
    def data(self) -> list:
        return self.__data
