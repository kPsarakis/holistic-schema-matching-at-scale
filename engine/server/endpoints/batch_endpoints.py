import uuid
from itertools import product
from timeit import default_timer
from typing import Dict, Optional, Iterator, Tuple

from celery import chord
from flask import request, jsonify, Blueprint
from more_itertools import unique_everseen

from engine.celery_tasks.tasks import merge_matches, get_matches_minio

from engine import app
from engine.utils.api_utils import MinioBulkPayload, get_minio_bulk_payload, validate_matcher


batch_endpoints = Blueprint('batch_endpoints', __name__)


@batch_endpoints.route('/matches/minio/submit_batch_job', methods=['POST'])
def submit_batch_job():
    job_uuid: str = str(uuid.uuid4())

    payload: MinioBulkPayload = get_minio_bulk_payload(request.json)
    app.logger.info(f"Retrieving data for job: {job_uuid}")

    algorithm: Dict[str, Optional[Dict[str, object]]]
    for algorithm in payload.algorithms:
        algorithm_name, algorithm_params = list(algorithm.items())[0]
        algorithm_uuid: str = job_uuid + "_" + algorithm_name
        validate_matcher(algorithm_name, algorithm_params, "minio")
        app.logger.info(f"Sending job: {algorithm_uuid} to Celery")

        combs = product(payload.source_tables, payload.target_tables)

        deduplicated_table_combinations: Iterator[Tuple[Tuple[str, str], Tuple[str, str]]] = unique_everseen([
            ((comb[0]['db_name'], comb[0]['table_name']), (comb[1]['db_name'], comb[1]['table_name']))
            for comb in combs
            if comb[0] != comb[1]], key=frozenset)

        start = default_timer()
        callback = merge_matches.s(algorithm_uuid, start)
        header = [get_matches_minio.s(algorithm_name, algorithm_params, *table_combination)
                  for table_combination in deduplicated_table_combinations]
        chord(header)(callback)

    return jsonify(job_uuid)
