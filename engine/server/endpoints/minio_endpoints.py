import uuid
from itertools import product
from tempfile import gettempdir
from typing import List
from os import path, environ

from celery import chord
from flask import request, abort, jsonify, Response, Blueprint
from minio import Minio
from minio.error import MinioException
from pandas.errors import EmptyDataError
from werkzeug.utils import secure_filename

from engine.data_sources.base_db import BaseDB
from engine.data_sources.base_source import GUIDMissing
from engine.data_sources.minio.minio_source import MinioSource
from engine.data_sources.minio.minio_table import MinioTable
from engine.forms import UploadFileToMinioForm
from engine.utils.api_utils import MinioPayload, get_minio_payload, validate_matcher

from engine.celery_tasks.tasks import merge_matches, get_matches_minio


minio_client: Minio = Minio('{host}:{port}'.format(host=environ['MINIO_HOST'],
                                                   port=environ['MINIO_PORT']),
                            access_key=environ['MINIO_ACCESS_KEY'],
                            secret_key=environ['MINIO_SECRET_KEY'],
                            secure=False)


minio_endpoints = Blueprint('minio_endpoints', __name__)


@minio_endpoints.route("/matches/minio/holistic", methods=['POST'])
def find_holistic_matches_of_table_minio():
    payload: MinioPayload = get_minio_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "minio")
    minio_source: MinioSource = MinioSource()
    try:
        dbs_tables_guids: List[List[str]] = [x.get_table_str_guids() for x in minio_source.get_all_dbs().values()]
        table: MinioTable = minio_source.get_db_table(payload.table_name, payload.db_name, load_data=False)
    except (GUIDMissing, MinioException):
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


@minio_endpoints.route('/matches/minio/other_db/<db_name>', methods=['POST'])
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
    except (GUIDMissing, MinioException):
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


@minio_endpoints.route('/matches/minio/within_db', methods=['POST'])
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
    except (GUIDMissing, MinioException):
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


@minio_endpoints.route('/matches/minio/ls', methods=['GET'])
def get_minio_dir_tree():
    return jsonify([{"db_name": bucket.name,
                     "tables": [obj.object_name for obj in minio_client.list_objects(bucket.name)]
                     }
                    for bucket in minio_client.list_buckets()])


@minio_endpoints.route('/matches/minio/column_sample/<db_name>/<table_name>/<column_name>', methods=['GET'])
def get_column_sample_minio(db_name: str, table_name: str, column_name: str):
    minio_source: MinioSource = MinioSource()
    return jsonify(minio_source.get_column_sample(db_name, table_name, column_name))


@minio_endpoints.route('/minio/create_bucket/<bucket_name>', methods=['POST'])
def create_minio_bucket(bucket_name: str):
    minio_client.make_bucket(bucket_name)
    return Response(f"Bucket {bucket_name} created successfully", status=200)


@minio_endpoints.route('/minio/upload_file/<bucket_name>', methods=['POST'])
def minio_upload_file(bucket_name: str):
    form = UploadFileToMinioForm()
    if not form.validate_on_submit():
        abort(400, form.errors)
    tmp_dir: str = gettempdir()
    filename = secure_filename(form.resource.data.filename)
    src_file = path.join(tmp_dir, filename)
    form.resource.data.save(src_file)
    minio_client.fput_object(bucket_name, filename, src_file)
    return Response(f"File {filename} uploaded in bucket {bucket_name} successfully", status=200)
