import os
from typing import Union, Dict

from minio import Minio, ResponseError

from .minio_database import MinioDatabase
from .minio_table import MinioTable
from .minio_utils import correct_file_ending
from ..atlas.atlas_source import GUIDMissing
from ..base_db import BaseDB
from ..base_source import BaseSource
from ...utils.utils import get_project_root


class MinioSource(BaseSource):

    def __init__(self):
        self.__minio_client = Minio('{host}:{port}'.format(host=os.environ['MINIO_HOST'],
                                                           port=os.environ['MINIO_PORT']),
                                    access_key=os.environ['MINIO_ACCESS_KEY'],
                                    secret_key=os.environ['MINIO_SECRET_KEY'],
                                    secure=False)
        self.__dbs: Dict[object, BaseDB] = dict()
        self.__db_guids: list = list(map(lambda bucket: bucket.name, self.__minio_client.list_buckets()))

    def get_db(self, guid: object) -> BaseDB:
        if guid not in self.__db_guids:
            raise GUIDMissing
        if guid not in self.__dbs:
            self.__dbs[guid] = MinioDatabase(self.__minio_client, str(guid))
        return self.__dbs[guid]

    def get_all_dbs(self) -> Dict[object, BaseDB]:
        for db_name in self.__db_guids:
            self.__dbs[db_name] = MinioDatabase(self.__minio_client, db_name)
        return self.__dbs

    def get_db_table(self, guid: object, db_guid: object = None) -> Union[MinioDatabase, MinioTable]:
        if db_guid is None:
            raise GUIDMissing
        try:
            local_tmp_minio_path = get_project_root() + '/tmp_minio_folder'
            correct_guid: str = correct_file_ending(str(guid))
            table_path: str = local_tmp_minio_path + '/' + correct_guid
            self.__minio_client.fget_object(db_guid, correct_guid, local_tmp_minio_path + '/' + correct_guid)
            table_name: str = correct_guid.split(".")[0]
            table: MinioTable = MinioTable(table_path, table_name, str(db_guid))
            os.remove(table_path)
        except ResponseError:
            raise GUIDMissing
        else:
            return table
