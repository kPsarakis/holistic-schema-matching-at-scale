import json
import os

from celery import Celery, chord
from celery.result import AsyncResult
from minio.error import NoSuchKey
from flask import Flask, request, abort, Response
from typing import Dict
from redis import Redis
from itertools import product

from engine.data_sources.atlas.atlas_table import AtlasTable
from engine.data_sources.base_source import GUIDMissing
from engine.data_sources.atlas.atlas_source import AtlasSource
from engine.data_sources.base_db import BaseDB
from engine.data_sources.base_table import BaseTable
from engine.data_sources.minio.minio_source import MinioSource
from engine.data_sources.minio.minio_table import MinioTable
from engine.utils.api_utils import AtlasPayload, get_atlas_payload, validate_matcher, get_atlas_source, \
     get_holistic_matches, format_matches, get_matcher, MinioPayload, get_minio_payload
from engine.utils.exceptions import check_if_table_has_columns, check_if_db_is_empty
from engine.utils.utils import get_sha1_hash_of_string, get_timestamp

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
app.config['CELERY_RESULT_BACKEND_URL'] = os.environ['CELERY_RESULT_BACKEND_URL']
app.config['CELERY_ACCEPT_CONTENT'] = ['pickle', 'json']
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND_URL'])
celery.conf.update(app.config)


# redis_db: Redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])


@celery.task(serializer='pickle')
def get_matches(matching_algorithm: str, algorithm_params: dict, target_table, source_table):
    matcher = get_matcher(matching_algorithm, algorithm_params)
    return matcher.get_matches(source_table, target_table)


@celery.task
def merge_matches(individual_matches: list, max_number_of_matches: int):
    merged_matches = [item for sublist in individual_matches for item in sublist]
    return sorted(merged_matches, key=lambda k: k['sim'], reverse=True)[:max_number_of_matches]


@app.route("/matches/atlas/holistic/<table_guid>", methods=['GET'])
def find_holistic_matches_of_table_atlas(table_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        check_if_table_has_columns(table)
        schemata: Dict[object, BaseDB] = atlas_src.get_all_dbs()
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
        matches = get_holistic_matches(schemata, table, payload)
        matching_jobs_guid = get_sha1_hash_of_string(
            get_timestamp() + '/atlas/holistic/' + str(table.unique_identifier))
        # redis_db.set(matching_jobs_guid, format_matches(matches, payload.max_number_matches))
        return matching_jobs_guid


@app.route('/matches/atlas/other_db/<table_guid>/<db_guid>', methods=['GET'])
def find_matches_other_db_atlas(table_guid: str, db_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        check_if_table_has_columns(table)
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
        check_if_db_is_empty(db)
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_tables().values(), table)]
        task: AsyncResult = chord(header)(callback)
        # matching_jobs_guid = get_sha1_hash_of_string(
        #     get_timestamp() + '/atlas/other_db/' + db_guid + str(table.unique_identifier))
        # redis_db.set(matching_jobs_guid, format_matches(matches, payload.max_number_matches))
        return Response("celery-task-meta-" + task.id, status=200)


@app.route('/matches/atlas/within_db/<table_guid>', methods=['GET'])
def find_matches_within_db_atlas(table_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        check_if_table_has_columns(table)
        db_schema: BaseDB = atlas_src.get_db(table.db_belongs_uid)
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
        r_table: BaseTable = db_schema.remove_table(table_guid)
        check_if_db_is_empty(db_schema)
        matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
        matches: list = matcher.get_matches(db_schema, table)
        # add the removed table back into the schema
        db_schema.add_table(r_table)
        matching_jobs_guid = get_sha1_hash_of_string(
            get_timestamp() + '/atlas/within_db/' + str(table.unique_identifier))
        # redis_db.set(matching_jobs_guid, format_matches(matches, payload.max_number_matches))
        return matching_jobs_guid


@app.route("/matches/minio/holistic", methods=['GET'])
def find_holistic_matches_of_table_minio():
    payload: MinioPayload = get_minio_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "minio")
    minio_source: MinioSource = MinioSource()
    try:
        table: MinioTable = minio_source.get_db_table(payload.table_name, payload.db_name)
        check_if_table_has_columns(table)
        dbs: Dict[object, BaseDB] = minio_source.get_all_dbs()
    except NoSuchKey:
        abort(400, "The table does not exist")
    else:
        matches = get_holistic_matches(dbs, table, payload)
        matching_jobs_guid = get_sha1_hash_of_string(
            get_timestamp() + '/minio/holistic/' + str(table.unique_identifier))
        # redis_db.set(matching_jobs_guid, format_matches(matches, payload.max_number_matches))
        return matching_jobs_guid


@app.route('/matches/minio/other_db/<db_name>', methods=['GET'])
def find_matches_other_db_minio(db_name: str):
    payload: MinioPayload = get_minio_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "minio")
    minio_source: MinioSource = MinioSource()
    try:
        table: MinioTable = minio_source.get_db_table(payload.table_name, payload.db_name)
        check_if_table_has_columns(table)
        db: BaseDB = minio_source.get_db(db_name)
    except NoSuchKey:
        abort(400, "The table does not exist")
    else:
        check_if_db_is_empty(db)
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_tables().values(), table)]
        task: AsyncResult = chord(header)(callback)
        # matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
        # matches: list = matcher.get_matches(db_schema, table)
        # matching_jobs_guid = get_sha1_hash_of_string(
        #     get_timestamp() + '/minio/other_db/' + db_name + str(table.unique_identifier))
        # redis_db.set(matching_jobs_guid, format_matches(matches, payload.max_number_matches))
        return Response("celery-task-meta-" + task.id, status=200)


@app.route('/matches/minio/within_db', methods=['GET'])
def find_matches_within_db_minio():
    payload: MinioPayload = get_minio_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "minio")
    minio_source: MinioSource = MinioSource()
    try:
        table: MinioTable = minio_source.get_db_table(payload.table_name, payload.db_name)
        check_if_table_has_columns(table)
        db: BaseDB = minio_source.get_db(table.db_belongs_uid)
    except NoSuchKey:
        abort(400, "The table does not exist")
    else:
        r_table: BaseTable = db.remove_table(payload.table_name)
        check_if_db_is_empty(db)
        callback = merge_matches.s(payload.max_number_matches)
        header = [get_matches.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_tables().values(), [table])]
        task: AsyncResult = chord(header)(callback)
        # matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
        # matches: list = matcher.get_matches(db_schema, table)
        # add the removed table back into the schema
        db.add_table(r_table)
        # matching_jobs_guid = get_sha1_hash_of_string(get_timestamp() +
        #                                              '/minio/within_db/' + str(table.unique_identifier))
        # redis_db.set(matching_jobs_guid, format_matches(matches, payload.max_number_matches))
        return Response("celery-task-meta-" + task.id, status=200)


if __name__ == '__main__':
    app.run(debug=False)
