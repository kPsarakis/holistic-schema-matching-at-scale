import os
from typing import Union, Dict

from minio import Minio, ResponseError

from .minio_database import MinioDatabase
from .minio_table import MinioTable
from ..atlas.atlas_source import GUIDMissing
from ..base_db import BaseDB
from ..base_source import BaseSource
from ..base_table import BaseTable


class MinioSource(BaseSource):

    def __init__(self):
        self.__minio_client = Minio(os.environ['MINIO_HOST'],
                                    access_key=os.environ['MINIO_ACCESS_KEY'],
                                    secret_key=os.environ['MINIO_SECRET_KEY'],
                                    secure=False)
        self.__dbs: Dict[object, BaseDB] = dict()
        self.__db_guids: list = list(map(lambda bucket: bucket.name, self.__minio_client.list_buckets()))

    def get_db(self, guid: object) -> BaseDB:
        if guid not in self.__db_guids:
            raise GUIDMissing
        if guid not in self.__dbs:
            self.__dbs[guid] = MinioDatabase(str(guid))  # FIXME
        return self.__dbs[guid]

    def get_all_dbs(self) -> Dict[object, BaseDB]:
        for db_name in self.__db_guids:
            self.__dbs[db_name] = MinioDatabase(db_name)  # FIXME
        return self.__dbs

    def get_db_table(self, guid: object, db_guid: object = None) -> Union[BaseDB, BaseTable]:
        if db_guid is None:
            raise GUIDMissing
        try:
            fget_object(db_guid, guid, 'data/' + str(guid))  # FIXME
        except ResponseError:
            raise GUIDMissing
        finally:
            return MinioTable()
