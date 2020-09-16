from flask import Flask, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/matches/minio/holistic", methods=['POST'])
def find_holistic_matches_of_table_minio():
    job_uuid = "1234567890"
    return jsonify(job_uuid)


@app.route('/matches/minio/other_db/<db_name>', methods=['POST'])
def find_matches_other_db_minio(db_name: str):
    job_uuid = "1234567890"
    return jsonify(job_uuid)


@app.route('/matches/minio/within_db', methods=['POST'])
def find_matches_within_db_minio():
    job_uuid = "1234567890"
    return jsonify(job_uuid)


@app.route('/results/finished_jobs', methods=['GET'])
def get_finished_jobs():
    example = ["abc", "def", "ghi", "abc", "def", "ghi", "abc", "def", "ghi", "abc", "def", "ghi"]
    return jsonify(example)


@app.route('/results/job_results/<job_id>', methods=['GET'])
def get_job_results(job_id: str):
    example = [{"source": {"tbl_nm": "source_table1", "tbl_guid": "source_table1",
                "clm_nm": "source_column1", "clm_guid": "source_column1"},
                "target": {"tbl_nm": "target_table1", "tbl_guid": "target_table1",
                           "clm_nm": "target_column1", "clm_guid": "target_column1"},
                "sim": 1},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.967456},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.834},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.7234},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.6},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.5},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.4},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.3},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.2},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.1},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8},
               {"source": {"tbl_nm": "source_table2", "tbl_guid": "source_table2",
                           "clm_nm": "source_column2", "clm_guid": "source_column2"},
                "target": {"tbl_nm": "target_table2", "tbl_guid": "target_table2",
                           "clm_nm": "target_column2", "clm_guid": "target_column2"},
                "sim": 0.8}]
    return jsonify(example)


@app.route('/results/save_verified_match/<job_id>/<index>', methods=['POST'])
def save_verified_match(job_id: str, index: int):
    return Response("All good", status=200)


@app.route('/results/discard_match/<job_id>/<index>', methods=['POST'])
def discard_match(job_id: str, index: int):
    return Response("All good", status=200)


@app.route('/results/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id: str):
    return Response("All good", status=200)


@app.route('/results/verified_matches', methods=['GET'])
def get_verified_matches():
    return get_job_results(0)


@app.route('/matches/minio/column_sample/<db_name>/<table_name>/<column_name>', methods=['GET'])
def get_column_sample_minio(db_name: str, table_name: str, column_name: str):
    example = ["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8", "test9", "test10"]
    return jsonify(example)


@app.route('/matches/minio/ls', methods=['GET'])
def get_minio_dir_tree():
    ls = [{"db_name": "db1", "tables": ["t1", "t2", "t3"]}, {"db_name": "db2", "tables": ["t4", "t5"]},
          {"db_name": "db3", "tables": []}]
    return jsonify(ls)


if __name__ == '__main__':
    app.run(debug=True)
