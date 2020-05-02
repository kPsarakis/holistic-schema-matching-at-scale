import os
from typing import Dict, Union

from engine.data_sources.atlas.atlas_source import GUIDMissing
from engine.data_sources.base_db import BaseDB
from engine.data_sources.base_source import BaseSource
from engine.data_sources.csv_store_source.csv_store_database import CSVStoreDatabase
from engine.data_sources.csv_store_source.csv_store_table import CSVStoreTable
from engine.data_sources.csv_store_source.csv_store_utils import get_folders_within_folder


class CSVStoreSource(BaseSource):

    def __init__(self, store_path: str):
        self.__store_path = store_path
        self.__dbs: Dict[object, BaseDB] = dict()
        self.__db_guids: list = get_folders_within_folder(store_path)

    def get_db(self, guid: object) -> BaseDB:
        if guid not in self.__db_guids:
            raise GUIDMissing
        if guid not in self.__dbs:
            self.__dbs[guid] = CSVStoreDatabase(self.__store_path + os.path.sep + str(guid), str(guid))
        return self.__dbs[guid]

    def get_all_dbs(self) -> Dict[object, BaseDB]:
        for db_name in self.__db_guids:
            self.__dbs[db_name] = CSVStoreDatabase(self.__store_path + os.path.sep + db_name, db_name)
        return self.__dbs

    def get_db_table(self, guid: object, db_guid: object = None) -> Union[CSVStoreDatabase, CSVStoreTable]:
        if db_guid is None:
            raise GUIDMissing
        for root, dirs, files in os.walk(os.path.join(self.__store_path+os.path.sep+str(db_guid))):
            for file in files:
                table_path: str = root + os.path.sep + file
                table_name: str = table_path.split(os.path.sep)[-1].split(".")[0]
                if table_name == guid:
                    return CSVStoreTable(table_path, table_name, str(db_guid))
        raise GUIDMissing
