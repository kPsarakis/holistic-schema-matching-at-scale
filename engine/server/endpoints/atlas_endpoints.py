import json
import uuid
from itertools import product
from typing import List

from celery import chord
from flask import request, abort, jsonify, Blueprint

from engine.data_sources.atlas.atlas_source import AtlasSource
from engine.data_sources.atlas.atlas_table import AtlasTable
from engine.data_sources.base_db import BaseDB
from engine.data_sources.base_source import GUIDMissing
from engine.utils.api_utils import AtlasPayload, get_atlas_payload, validate_matcher, get_atlas_source

from engine.celery_tasks.tasks import merge_matches, get_matches_atlas


atlas_endpoints = Blueprint('atlas_endpoints', __name__)


@atlas_endpoints.route("/matches/atlas/holistic/<table_guid>", methods=['POST'])
def find_holistic_matches_of_table_atlas(table_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        if table.is_empty:
            abort(400, "The table does not have any columns")
        dbs_tables_guids: List[List[str]] = [x.get_table_str_guids() for x in atlas_src.get_all_dbs().values()]
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


@atlas_endpoints.route('/matches/atlas/other_db/<table_guid>/<db_guid>', methods=['POST'])
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


@atlas_endpoints.route('/matches/atlas/within_db/<table_guid>', methods=['POST'])
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
