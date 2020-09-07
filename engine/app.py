import json
import os
import uuid

from celery import Celery, chord
from minio.error import NoSuchKey
from flask import Flask, request, abort, jsonify, Response
from typing import List
from itertools import product

from pandas.errors import EmptyDataError
from redis import Redis

from engine.algorithms.algorithms import schema_only_algorithms
from engine.data_sources.atlas.atlas_table import AtlasTable
from engine.data_sources.base_source import GUIDMissing
from engine.data_sources.atlas.atlas_source import AtlasSource
from engine.data_sources.base_db import BaseDB
from engine.data_sources.minio.minio_source import MinioSource
from engine.data_sources.minio.minio_table import MinioTable
from engine.utils.api_utils import AtlasPayload, get_atlas_payload, validate_matcher, get_atlas_source, get_matcher, \
    MinioPayload, get_minio_payload

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://{user}:{pwd}@{host}:{port}/'.format(user=os.environ['RABBITMQ_DEFAULT_USER'],
                                                                              pwd=os.environ['RABBITMQ_DEFAULT_PASS'],
                                                                              host=os.environ['RABBITMQ_HOST'],
                                                                              port=os.environ['RABBITMQ_PORT'])
app.config['CELERY_RESULT_BACKEND_URL'] = 'redis://{host}:{port}/'.format(host=os.environ['CELERY_RESULTS_REDIS_HOST'],
                                                                          port=os.environ['CELERY_RESULTS_REDIS_PORT'])
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND_URL'])
celery.conf.update(app.config)
celery.conf.update(task_serializer='json',
                   accept_content=['json'],
                   result_serializer='json')

match_result_db: Redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], charset="utf-8",
                               decode_responses=True, db=0)
insertion_order_db: Redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], charset="utf-8",
                                  decode_responses=True, db=1)
verified_match_db: Redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], charset="utf-8",
                                 decode_responses=True, db=2)


@celery.task
def get_matches_minio(matching_algorithm: str, algorithm_params: dict, target_table: tuple, source_table: tuple):
    matcher = get_matcher(matching_algorithm, algorithm_params)
    minio_source: MinioSource = MinioSource()
    target_db_name, target_table_name = target_table
    source_db_name, source_table_name = source_table
    load_data = False if matching_algorithm in schema_only_algorithms else True
    target_minio_table: MinioTable = minio_source.get_db_table(target_table_name, target_db_name, load_data=load_data)
    source_minio_table: MinioTable = minio_source.get_db_table(source_table_name, source_db_name, load_data=load_data)
    return matcher.get_matches(source_minio_table, target_minio_table)


@celery.task
def get_matches_atlas(matching_algorithm: str, algorithm_params: dict, target_table_guid: str, source_table_guid: str,
                      rj):
    payload: AtlasPayload = get_atlas_payload(rj)
    matcher = get_matcher(matching_algorithm, algorithm_params)
    atlas_source: AtlasSource = get_atlas_source(payload)
    target_atlas_table: AtlasTable = atlas_source.get_db_table(target_table_guid)
    source_atlas_table: AtlasTable = atlas_source.get_db_table(source_table_guid)
    return matcher.get_matches(source_atlas_table, target_atlas_table)


@celery.task
def merge_matches(individual_matches: list, job_uuid: str, max_number_of_matches: int = 1000):
    merged_matches = [item for sublist in individual_matches for item in sublist]
    sorted_matches = sorted(merged_matches, key=lambda k: k['sim'], reverse=True)[:max_number_of_matches]
    insertion_order_db.rpush('insertion_ordered_ids', job_uuid)
    match_result_db.set(job_uuid, json.dumps(sorted_matches))
    return sorted_matches


@app.route("/matches/atlas/holistic/<table_guid>", methods=['POST'])
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
        job_uuid: str = str(uuid.uuid4())
        callback = merge_matches.s(job_uuid, payload.max_number_matches)
        header = [get_matches_atlas.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination,
                                      request.json)
                  for table_combination in
                  product([item for sublist in dbs_tables_guids for item in sublist], [table.unique_identifier])]
        chord(header)(callback)
        return jsonify(job_uuid)


@app.route('/matches/atlas/other_db/<table_guid>/<db_guid>', methods=['POST'])
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
        job_uuid: str = str(uuid.uuid4())
        callback = merge_matches.s(job_uuid, payload.max_number_matches)
        header = [get_matches_atlas.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination,
                                      request.json)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        chord(header)(callback)
        return jsonify(job_uuid)


@app.route('/matches/atlas/within_db/<table_guid>', methods=['POST'])
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
        job_uuid: str = str(uuid.uuid4())
        callback = merge_matches.s(job_uuid, payload.max_number_matches)
        header = [get_matches_atlas.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination,
                                      request.json)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        chord(header)(callback)
        return jsonify(job_uuid)


@app.route("/matches/minio/holistic", methods=['POST'])
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
        job_uuid: str = str(uuid.uuid4())
        callback = merge_matches.s(job_uuid, payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in
                  product([item for sublist in dbs_tables_guids for item in sublist], [table.unique_identifier])]
        chord(header)(callback)
        return jsonify(job_uuid)


@app.route('/matches/minio/other_db/<db_name>', methods=['POST'])
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
        job_uuid: str = str(uuid.uuid4())
        callback = merge_matches.s(job_uuid, payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        chord(header)(callback)
        return jsonify(job_uuid)


@app.route('/matches/minio/within_db', methods=['POST'])
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
        job_uuid: str = str(uuid.uuid4())
        callback = merge_matches.s(job_uuid, payload.max_number_matches)
        header = [get_matches_minio.s(payload.matching_algorithm, payload.matching_algorithm_params, *table_combination)
                  for table_combination in product(db.get_table_str_guids(), [table.unique_identifier])]
        chord(header)(callback)
        return jsonify(job_uuid)


@app.route('/results/finished_jobs', methods=['GET'])
def get_finished_jobs():
    return jsonify(insertion_order_db.lrange('insertion_ordered_ids', 0, -1))


@app.route('/results/job_results/<job_id>', methods=['GET'])
def get_job_results(job_id: str):
    results = match_result_db.get(job_id)
    if results is None:
        return Response("Job does not exist", status=400)
    return jsonify(json.loads(results))


@app.route('/results/save_verified_match/<job_id>/<index>', methods=['POST'])
def save_verified_match(job_id: str, index: int):
    results = match_result_db.get(job_id)
    if results is None:
        return Response("Job does not exist", status=400)
    ranked_list: list = json.loads(results)
    try:
        to_save = ranked_list.pop(int(index))
    except IndexError:
        return Response("Match does not exist", status=400)
    verified_matches = list(map(lambda x: json.loads(x), verified_match_db.lrange('verified_matches', 0, -1)))
    if to_save in verified_matches:
        return Response("Match already verified", status=200)
    verified_match_db.rpush('verified_matches', json.dumps(to_save))
    match_result_db.set(job_id, json.dumps(ranked_list))
    return Response("Matched saved successfully", status=200)


@app.route('/results/discard_match/<job_id>/<index>', methods=['POST'])
def discard_match(job_id: str, index: int):
    results = match_result_db.get(job_id)
    if results is None:
        return Response("Job does not exist", status=400)
    ranked_list: list = json.loads(results)
    try:
        ranked_list.pop(int(index))
    except IndexError:
        return Response("Match does not exist", status=400)
    match_result_db.set(job_id, json.dumps(ranked_list))
    return Response("Matched discarded successfully", status=200)


@app.route('/results/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id: str):
    match_result_db.delete(job_id)
    insertion_order_db.lrem('insertion_ordered_ids', 1, job_id)
    return Response("Job discarded successfully", status=200)


@app.route('/results/verified_matches', methods=['GET'])
def get_verified_matches():
    return jsonify(list(map(lambda x: json.loads(x), verified_match_db.lrange('verified_matches', 0, -1))))


if __name__ == '__main__':
    app.run(debug=False)
