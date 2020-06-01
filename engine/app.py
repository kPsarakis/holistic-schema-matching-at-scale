import json
import os

from celery import Celery, chord
from celery.result import AsyncResult
from minio.error import NoSuchKey
from flask import Flask, request, abort, Response
from typing import List
from itertools import product

from pandas.errors import EmptyDataError

from engine.data_sources.atlas.atlas_table import AtlasTable
from engine.data_sources.base_source import GUIDMissing
from engine.data_sources.atlas.atlas_source import AtlasSource
from engine.data_sources.base_db import BaseDB
from engine.data_sources.minio.minio_source import MinioSource
from engine.data_sources.minio.minio_table import MinioTable
from engine.utils.api_utils import AtlasPayload, get_atlas_payload, validate_matcher, get_atlas_source, \
    get_matcher, MinioPayload, get_minio_payload

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
app.config['CELERY_RESULT_BACKEND_URL'] = os.environ['CELERY_RESULT_BACKEND_URL']
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND_URL'])
celery.conf.update(app.config)
celery.conf.update(task_serializer='json',
                   accept_content=['json'],
                   result_serializer='json')


@celery.task
def get_matches_minio(matching_algorithm: str, algorithm_params: dict, target_table: tuple, source_table: tuple):
    matcher = get_matcher(matching_algorithm, algorithm_params)
    minio_source: MinioSource = MinioSource()
    target_db_name, target_table_name = target_table
    source_db_name, source_table_name = source_table
    target_minio_table: MinioTable = minio_source.get_db_table(target_table_name, target_db_name)
    source_minio_table: MinioTable = minio_source.get_db_table(source_table_name, source_db_name)
    return matcher.get_matches(source_minio_table, target_minio_table)


@celery.task
def get_matches_atlas(matching_algorithm: str, algorithm_params: dict, target_table: tuple, source_table: tuple,
                      payload):
    matcher = get_matcher(matching_algorithm, algorithm_params)
    atlas_source: AtlasSource = get_atlas_source(payload)
    target_db_name, target_table_name = target_table
    source_db_name, source_table_name = source_table
    target_minio_table: AtlasTable = atlas_source.get_db_table(target_table_name, target_db_name)
    source_minio_table: AtlasTable = atlas_source.get_db_table(source_table_name, source_db_name)
    return matcher.get_matches(source_minio_table, target_minio_table)


@celery.task
def merge_matches(individual_matches: list, max_number_of_matches: int = 1000):
    merged_matches = [item for sublist in individual_matches for item in sublist]
    return sorted(merged_matches, key=lambda k: k['sim'], reverse=True)[:max_number_of_matches]


@app.route("/matches/atlas/holistic/<table_guid>", methods=['GET'])
def find_holistic_matches_of_table_atlas(table_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        if table.is_empty:
            abort(400, "The table does not have any columns")
        dbs_tables_guids: List[List[str]] = list(map(lambda x: x.get_table_str_guids(),
                                                     atlas_src.get_all_dbs().values()))
    except json.JSONDecodeError:
        abort(500, "Couldn't connect to Atlas. This is a network issue, "
                   "try to lower the request_chunk_size and the request_parallelism in the payload")
    except GUIDMissing:
        abort(400, 'This guid does not correspond to any database in atlas! '
                   'Check if the given database types are correct or if there is a mistake in the guid')
    except KeyError:
        abort(400, 'This guid does not correspond to any table in atlas! '
                   'Check if the given table types are correct or if there is a mistake in the guid')
    else:
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in
                  product([item for sublist in dbs_tables_guids for item in sublist], [table.unique_identifier])]
        task: AsyncResult = chord(header)(callback)
        return Response("celery-task-meta-" + task.id, status=200)


@app.route('/matches/atlas/other_db/<table_guid>/<db_guid>', methods=['GET'])
def find_matches_other_db_atlas(table_guid: str, db_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        if table.is_empty:
            abort(400, "The table does not have any columns")
        db: BaseDB = atlas_src.get_db(db_guid)
    except json.JSONDecodeError:
        abort(500, "Couldn't connect to Atlas. This is a network issue, "
                   "try to lower the request_chunk_size and the request_parallelism in the payload")
    except GUIDMissing:
        abort(400, 'This guid does not correspond to any database in atlas! '
                   'Check if the given database types are correct or if there is a mistake in the guid')
    except KeyError:
        abort(400, 'This guid does not correspond to any table in atlas! '
                   'Check if the given table types are correct or if there is a mistake in the guid')
    else:
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        task: AsyncResult = chord(header)(callback)
        return Response("celery-task-meta-" + task.id, status=200)


@app.route('/matches/atlas/within_db/<table_guid>', methods=['GET'])
def find_matches_within_db_atlas(table_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        if table.is_empty:
            abort(400, "The table does not have any columns")
        db: BaseDB = atlas_src.get_db(table.db_belongs_uid)
        if db.number_of_tables == 1:
            abort(400, "The given db only contains one table")
    except json.JSONDecodeError:
        abort(500, "Couldn't connect to Atlas. This is a network issue, "
                   "try to lower the request_chunk_size and the request_parallelism in the payload")
    except GUIDMissing:
        abort(400, 'This guid does not correspond to any database in atlas! '
                   'Check if the given database types are correct or if there is a mistake in the guid')
    except KeyError:
        abort(400, 'This guid does not correspond to any table in atlas! '
                   'Check if the given table types are correct or if there is a mistake in the guid')
    else:
        # remove the table from the schema so that it doesn't compare against itself
        db.remove_table(table_guid)
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        task: AsyncResult = chord(header)(callback)
        return Response("celery-task-meta-" + task.id, status=200)


@app.route("/matches/minio/holistic", methods=['GET'])
def find_holistic_matches_of_table_minio():
    payload: MinioPayload = get_minio_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "minio")
    minio_source: MinioSource = MinioSource()
    try:
        dbs_tables_guids: List[List[str]] = list(map(lambda x: x.get_table_str_guids(),
                                                     minio_source.get_all_dbs().values()))
        table: MinioTable = minio_source.get_db_table(payload.table_name, payload.db_name, load_data=False)
    except (GUIDMissing, NoSuchKey):
        abort(400, "The table does not exist")
    except EmptyDataError:
        abort(400, "The table does not contain any columns")
    else:
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in
                  product([item for sublist in dbs_tables_guids for item in sublist], [table.unique_identifier])]
        task: AsyncResult = chord(header)(callback)
        return Response("celery-task-meta-" + task.id, status=200)


@app.route('/matches/minio/other_db/<db_name>', methods=['GET'])
def find_matches_other_db_minio(db_name: str):
    payload: MinioPayload = get_minio_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "minio")
    minio_source: MinioSource = MinioSource()
    if not minio_source.contains_db(payload.db_name):
        abort(400, "The source does not contain the given database")
    try:
        db: BaseDB = minio_source.get_db(db_name, load_data=False)
        if db.is_empty:
            abort(400, "The given db does not contain any tables")
        table: MinioTable = minio_source.get_db_table(payload.table_name, payload.db_name, load_data=False)
    except (GUIDMissing, NoSuchKey):
        abort(400, "The table does not exist")
    except EmptyDataError:
        abort(400, "The table does not contain any columns")
    else:
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        task: AsyncResult = chord(header)(callback)
        return Response("celery-task-meta-" + task.id, status=200)


@app.route('/matches/minio/within_db', methods=['GET'])
def find_matches_within_db_minio():
    payload: MinioPayload = get_minio_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "minio")
    minio_source: MinioSource = MinioSource()
    if not minio_source.contains_db(payload.db_name):
        abort(400, "The source does not contain the given database")
    try:
        db: BaseDB = minio_source.get_db(payload.db_name, load_data=False)
        if db.is_empty:
            abort(400, "The given db does not contain any tables")
        if db.number_of_tables == 1:
            abort(400, "The given db only contains one table")
        table: MinioTable = minio_source.get_db_table(payload.table_name, payload.db_name, load_data=False)
    except (GUIDMissing, NoSuchKey):
        abort(400, "The table does not exist")
    except EmptyDataError:
        abort(400, "The table does not contain any columns")
    else:
        db.remove_table(payload.table_name)
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        task: AsyncResult = chord(header)(callback)
        return Response("celery-task-meta-" + task.id, status=200)


if __name__ == '__main__':
    app.run(debug=False)
