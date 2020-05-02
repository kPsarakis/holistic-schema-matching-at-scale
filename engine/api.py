from json import JSONDecodeError
from pathlib import Path

from flask import Flask, request, abort, Response, jsonify
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Optional, Union
from werkzeug.utils import secure_filename
import os

import engine.algorithms.algorithms as module_algorithms
from engine.algorithms.algorithms import schema_only_algorithms, instance_only_algorithms, schema_instance_algorithms
from engine.algorithms.base_matcher import BaseMatcher
from engine.data_sources.atlas.atlas_table import AtlasTable
from engine.data_sources.base_db import BaseDB
from engine.data_sources.atlas.atlas_source import AtlasSource, GUIDMissing
from engine.data_sources.base_table import BaseTable
from engine.data_sources.csv_store_source.csv_store_source import CSVStoreSource
from engine.data_sources.csv_store_source.csv_store_table import CSVStoreTable
from engine.utils.exceptions import check_if_table_has_columns, check_if_db_is_empty
from engine.utils.utils import get_project_root, create_folder, allowed_csv_file, allowed_xlsx_file, xlsx_to_csvs, \
    directory_tree


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


class CSVStorePayload(BaseModel):
    table_name: str  # Table name is the Csv file name in the store
    db_name: str  # DB name is the name of the folder that it is under
    matching_algorithm: str
    # the maximum number of matches to be given as output
    max_number_matches: int = 1000
    # if the algorithm params are left empty the defaults will be chosen
    matching_algorithm_params: Optional[Dict[str, object]]

    class Config:
        arbitrary_types_allowed: bool = True


UPLOAD_FOLDER = get_project_root() + '/data/csv_file_store'  # The folder that will contain the csv file store

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False  # this is needed for the sorted list output because we sort by value
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 104857600  # set 100MB as the maximum csv file size


@app.route("/matches/atlas/holistic/<table_guid>", methods=['GET'])
def find_holistic_matches_of_table_atlas(table_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        check_if_table_has_columns(table)
        schemata: Dict[object, BaseDB] = atlas_src.get_all_dbs()
    except JSONDecodeError:
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
        return format_matches(matches, payload.max_number_matches)


@app.route('/matches/atlas/other_db/<table_guid>/<db_guid>', methods=['GET'])
def find_matches_other_db_atlas(table_guid: str, db_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        check_if_table_has_columns(table)
        db_schema: BaseDB = atlas_src.get_db(db_guid)
    except JSONDecodeError:
        abort(500, "Couldn't connect to Atlas. This is a network issue, "
                   "try to lower the request_chunk_size and the request_parallelism in the payload")
    except GUIDMissing:
        abort(400, 'This guid does not correspond to any database in atlas! '
                   'Check if the given database types are correct or if there is a mistake in the guid')
    except KeyError:
        abort(400, 'This guid does not correspond to any table in atlas! '
                   'Check if the given table types are correct or if there is a mistake in the guid')
    else:
        check_if_db_is_empty(db_schema)
        matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
        matches: list = matcher.get_matches(db_schema, table)
        return format_matches(matches, payload.max_number_matches)


@app.route('/matches/atlas/within_db/<table_guid>', methods=['GET'])
def find_matches_within_db_atlas(table_guid: str):
    payload: AtlasPayload = get_atlas_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "atlas")
    atlas_src: AtlasSource = get_atlas_source(payload)
    try:
        table: AtlasTable = atlas_src.get_db_table(table_guid)
        check_if_table_has_columns(table)
        db_schema: BaseDB = atlas_src.get_db(table.db_belongs_uid)
    except JSONDecodeError:
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
        return format_matches(matches, payload.max_number_matches)


@app.route("/matches/csv_store/holistic", methods=['GET'])
def find_holistic_matches_of_table_csv():
    payload: CSVStorePayload = get_csv_store_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "csv_store")
    csv_store_src: CSVStoreSource = get_csv_store_source(app.config['UPLOAD_FOLDER'])
    try:
        table: CSVStoreTable = csv_store_src.get_db_table(payload.table_name, payload.db_name)
        check_if_table_has_columns(table)
        dbs: Dict[object, BaseDB] = csv_store_src.get_all_dbs()
    except OSError:
        abort(400, "The table does not exist")
    else:
        matches = get_holistic_matches(dbs, table, payload)
        return format_matches(matches, payload.max_number_matches)


@app.route('/matches/csv_store/other_db/<db_name>', methods=['GET'])
def find_matches_other_db_csv(db_name: str):
    payload: CSVStorePayload = get_csv_store_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "csv_store")
    csv_store_src: CSVStoreSource = get_csv_store_source(app.config['UPLOAD_FOLDER'])
    try:
        table: CSVStoreTable = csv_store_src.get_db_table(payload.table_name, payload.db_name)
        check_if_table_has_columns(table)
        db_schema: BaseDB = csv_store_src.get_db(db_name)
    except OSError:
        abort(400, "The table does not exist")
    else:
        check_if_db_is_empty(db_schema)
        matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
        matches: list = matcher.get_matches(db_schema, table)
        return format_matches(matches, payload.max_number_matches)


@app.route('/matches/csv_store/within_db', methods=['GET'])
def find_matches_within_db_csv():
    payload: CSVStorePayload = get_csv_store_payload(request.json)
    validate_matcher(payload.matching_algorithm, payload.matching_algorithm_params, "csv_store")
    csv_store_src: CSVStoreSource = get_csv_store_source(app.config['UPLOAD_FOLDER'])
    try:
        table: CSVStoreTable = csv_store_src.get_db_table(payload.table_name, payload.db_name)
        check_if_table_has_columns(table)
        db_schema: BaseDB = csv_store_src.get_db(table.db_belongs_uid)
    except OSError:
        abort(400, "The table does not exist")
    else:
        r_table: BaseTable = db_schema.remove_table(payload.table_name)
        check_if_db_is_empty(db_schema)
        matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
        matches: list = matcher.get_matches(db_schema, table)
        # add the removed table back into the schema
        db_schema.add_table(r_table)
        return format_matches(matches, payload.max_number_matches)


@app.route('/matches/csv_store/upload_csv/<db_name>', methods=['POST'])
def upload_csv_file(db_name: str):
    create_folder(app.config['UPLOAD_FOLDER'])
    if 'file' not in request.files:
        abort(400, "No file part in the request")
    file = request.files['file']
    if file.filename == '':
        abort(400, "No file selected for uploading")
    if file and allowed_csv_file(file.filename):
        create_folder(app.config['UPLOAD_FOLDER']+os.path.sep+db_name)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER']+os.path.sep+db_name, filename))
        return Response("File successfully uploaded", status=201)
    else:
        abort(400, "The file must be in csv format")


@app.route('/matches/csv_store/upload_xlsx', methods=['POST'])
def upload_xlsx_file():
    create_folder(app.config['UPLOAD_FOLDER'])
    if 'file' not in request.files:
        abort(400, "No file part in the request")
    file = request.files['file']
    if file.filename == '':
        abort(400, "No file selected for uploading")
    if file and allowed_xlsx_file(file.filename):
        filename = secure_filename(file.filename)
        tmp_xlsx_file_path = app.config['UPLOAD_FOLDER'] + os.path.sep + '..' + os.path.sep + 'tmp_xlsx_files'
        create_folder(tmp_xlsx_file_path)
        file.save(os.path.join(tmp_xlsx_file_path, filename))
        db_name = filename.split(".xlsx")[0]
        xlsx_to_csvs(tmp_xlsx_file_path+os.path.sep+filename, db_name, app.config['UPLOAD_FOLDER'])
        os.remove(tmp_xlsx_file_path+os.path.sep+filename)
        return Response("File successfully uploaded", status=201)
    else:
        abort(400, "The file must be in xlsx format")


@app.route('/matches/csv_store/show', methods=['GET'])
def show_csv_store():
    output_str = 'The first level represents a database and the second a table in csv format\n' \
                 '--------------------------------------------------------------------------\n'
    for line in directory_tree(Path(app.config['UPLOAD_FOLDER'])):
        output_str += line + '\n'
    return Response(output_str, status=200)


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
        abort(400, "The algorithm does not exist (Check if the name was wrongly typed)")
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


def get_csv_store_payload(request_json: dict) -> CSVStorePayload:
    try:
        payload = CSVStorePayload(**request_json)
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
    except JSONDecodeError:
        abort(500, "Couldn't connect to Atlas. Check the given atlas url and credentials. "
                   "If they are correct, it is a network issue")
    except KeyError:
        abort(400, "One or more of the given database types does not exist or has a typo")
    else:
        return atlas_source


def get_csv_store_source(store_path: str) -> CSVStoreSource:
    try:
        csv_store_source: CSVStoreSource = CSVStoreSource(store_path)
    except OSError:
        abort(400, "The CSV store does not exist")
    else:
        return csv_store_source


def get_matcher(name, args) -> BaseMatcher:
    return getattr(module_algorithms, name)() if args is None else getattr(module_algorithms, name)(**dict(args))


def format_matches(matches: list, max_number_matches: int = 1000):
    matches = sorted(matches, key=lambda k: k['sim'], reverse=True)[:max_number_matches]
    return jsonify(matches)


def get_holistic_matches(dbs: Dict[object, BaseDB], table: BaseTable, payload: Union[AtlasPayload, CSVStorePayload]):
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


if __name__ == '__main__':
    app.run(debug=False)
