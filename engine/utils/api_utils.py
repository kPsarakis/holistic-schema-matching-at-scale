import json
from itertools import product
from typing import List, Optional, Dict, Union
from flask import abort
from pydantic import ValidationError, BaseModel

from ..algorithms.algorithms import schema_only_algorithms, instance_only_algorithms, schema_instance_algorithms
from ..algorithms.base_matcher import BaseMatcher
from ..data_sources.atlas.atlas_source import AtlasSource
from ..data_sources.atlas.atlas_table import AtlasTable
from ..data_sources.base_db import BaseDB
from ..data_sources.base_table import BaseTable
from ..data_sources.minio.minio_table import MinioTable

from engine.algorithms import algorithms as module_algorithms


class AtlasPayload(BaseModel):
    atlas_url: str
    atlas_username: str
    atlas_password: str
    db_types: List[str]
    matching_algorithm: str
    # the maximum number of matches to be given as output
    max_number_matches: int = 1000
    # increase the request_parallelism and request_chunk_size for faster data ingestion from atlas the default
    # values are low enough to work with a very slow internet connection.
    # request_parallelism is how many parallel requests the framework makes to atlas
    # request_chunk_size is how many entities the framework requests at once
    request_parallelism: int = 4
    request_chunk_size: int = 10
    # if the algorithm params are left empty the defaults will be chosen
    matching_algorithm_params: Optional[Dict[str, object]]

    class Config:
        arbitrary_types_allowed: bool = True


class MinioPayload(BaseModel):
    table_name: str  # Table name is the Csv file name in the store
    db_name: str  # DB name is the name of the folder that it is under
    matching_algorithm: str
    # the maximum number of matches to be given as output
    max_number_matches: int = 1000
    # if the algorithm params are left empty the defaults will be chosen
    matching_algorithm_params: Optional[Dict[str, object]]

    class Config:
        arbitrary_types_allowed: bool = True


def validate_matcher(name, args, endpoint):
    """
    Validates the matching algorithm params for early failure in the matching process if something is wrong
    """
    try:
        if name not in schema_only_algorithms + instance_only_algorithms + schema_instance_algorithms:
            abort(400, "The selected algorithm does not exist")
        if endpoint == "atlas" and (name not in schema_only_algorithms
                                    and not (name == "Coma" and
                                             (args is None or len(args) == 0 or args["strategy"] == "COMA_OPT"))):
            abort(400, "The selected algorithm requires data instances which atlas cannot provide")
        get_matcher(name, args)
    except AttributeError:
        abort(400, "The selected algorithm does not exist")
    except TypeError:
        abort(400, "Invalid matching algorithm parameters")


def get_atlas_payload(request_json: dict) -> AtlasPayload:
    try:
        payload = AtlasPayload(**request_json)
    except ValidationError:
        abort(400, "Incorrect payload arguments. Make sure that they contain the correct atlas_url: str, "
                   "atlas_username: str, atlas_password: str, db_types: List[str] and matching_algorithm: str")
    else:
        return payload


def get_minio_payload(request_json: dict) -> MinioPayload:
    try:
        payload = MinioPayload(**request_json)
    except ValidationError:
        abort(400, "Incorrect payload arguments. Make sure that they contain the correct table_name: str and "
                   "db_name: str of the table that you want to find the matches.")
    else:
        return payload


def get_atlas_source(payload: AtlasPayload) -> AtlasSource:
    try:
        atlas_source: AtlasSource = AtlasSource(payload.atlas_url, payload.atlas_username, payload.atlas_password,
                                                payload.db_types, payload.request_parallelism,
                                                payload.request_chunk_size)
    except json.JSONDecodeError:
        abort(500, "Couldn't connect to Atlas. Check the given atlas url and credentials. "
                   "If they are correct, it is a network issue")
    except KeyError:
        abort(400, "One or more of the given database types does not exist or has a typo")
    else:
        return atlas_source


def get_matcher(name, args) -> BaseMatcher:
    return getattr(module_algorithms, name)() if args is None else getattr(module_algorithms, name)(**dict(args))


def format_matches(matches: list, max_number_matches: int = 1000):
    matches = sorted(matches, key=lambda k: k['sim'], reverse=True)[:max_number_matches]
    return json.dumps(matches)


def get_holistic_matches(dbs: Dict[object, BaseDB], table: Union[AtlasTable, MinioTable],
                         payload: Union[AtlasPayload, MinioPayload]):
    r_table: BaseTable = dbs[table.db_belongs_uid].remove_table(payload.table_name)
    matches = []
    for db in dbs.values():
        if db.number_of_columns == 0:
            continue
        matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
        current_schema_matches = matcher.get_matches(db, table)
        current_schema_matches = sorted(current_schema_matches, key=lambda k: k['sim'],
                                        reverse=True)[:payload.max_number_matches // 2]
        matches.extend(current_schema_matches)
    dbs[table.db_belongs_uid].add_table(r_table)
    return matches
