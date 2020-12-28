import gzip
import json

from flask import jsonify, Response, Blueprint

from engine.db import insertion_order_db, match_result_db, runtime_db, verified_match_db


database_endpoints = Blueprint('database_endpoints', __name__)


@database_endpoints.route('/results/finished_jobs', methods=['GET'])
def get_finished_jobs():
    return jsonify(insertion_order_db.lrange('insertion_ordered_ids', 0, -1))


@database_endpoints.route('/results/job_results/<job_id>', methods=['GET'])
def get_job_results(job_id: str):
    results = json.loads(gzip.decompress(match_result_db.get(job_id)))
    if results is None:
        return Response("Job does not exist", status=400)
    return jsonify(results)


@database_endpoints.route('/results/job_runtime/<job_id>', methods=['GET'])
def get_job_runtime(job_id: str):
    results = runtime_db.get(job_id)
    if results is None:
        return Response("Job does not exist", status=400)
    return jsonify(json.loads(results))


@database_endpoints.route('/results/save_verified_match/<job_id>/<index>', methods=['POST'])
def save_verified_match(job_id: str, index: int):
    results = match_result_db.get(job_id)
    if results is None:
        return Response("Job does not exist", status=400)
    ranked_list: list = json.loads(gzip.decompress(results))
    try:
        to_save = ranked_list.pop(int(index))
    except IndexError:
        return Response("Match does not exist", status=400)
    verified_matches = [json.loads(x) for x in verified_match_db.lrange('verified_matches', 0, -1)]
    match_result_db.set(job_id, gzip.compress(json.dumps(ranked_list).encode('gbk')))
    if to_save in verified_matches:
        return Response("Match already verified", status=200)
    verified_match_db.rpush('verified_matches', json.dumps(to_save))
    return Response("Matched saved successfully", status=200)


@database_endpoints.route('/results/discard_match/<job_id>/<index>', methods=['POST'])
def discard_match(job_id: str, index: int):
    results = match_result_db.get(job_id)
    if results is None:
        return Response("Job does not exist", status=400)
    ranked_list: list = json.loads(gzip.decompress(results))
    try:
        ranked_list.pop(int(index))
    except IndexError:
        return Response("Match does not exist", status=400)
    match_result_db.set(job_id, gzip.compress(json.dumps(ranked_list).encode('gbk')))
    return Response("Matched discarded successfully", status=200)


@database_endpoints.route('/results/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id: str):
    match_result_db.delete(job_id)
    insertion_order_db.lrem('insertion_ordered_ids', 1, job_id)
    return Response("Job discarded successfully", status=200)


@database_endpoints.route('/results/verified_matches', methods=['GET'])
def get_verified_matches():
    verified_matches = [json.loads(x) for x in verified_match_db.lrange('verified_matches', 0, -1)]
    return jsonify(verified_matches)
