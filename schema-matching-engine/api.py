from json import JSONDecodeError
from pathlib import Path

from flask import Flask, request, abort, Response, jsonify
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Optional
from werkzeug.utils import secure_filename
import os

import algorithms.algorithms as module_algorithms
from algorithms.algorithms import schema_only_algorithms, instance_only_algorithms, schema_instance_algorithms
from algorithms.base_matcher import BaseMatcher
from data_sources.atlas.atlas_table import AtlasTable
from data_sources.base_db import BaseDB
from data_sources.atlas.atlas_source import AtlasSource, GUIDMissing
from data_sources.base_table import BaseTable
from data_sources.csv_store_source.csv_store_source import CSVStoreSource
from data_sources.csv_store_source.csv_store_table import CSVStoreTable
from utils.exceptions import check_if_table_has_columns, check_if_db_is_empty
from utils.utils import get_project_root, create_folder, allowed_csv_file, allowed_xlsx_file, xlsx_to_csvs, \
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
    """ Route that returns the holistic matches of a table in atlas
    ---
    get:
        summary: Endpoint that finds matches in atlas, of a table against all other tables.
        description: Get all the matches of a table within atlas
        parameters:
            - name: table_guid
              in: path
              description: the guid of the table that we want to find matches
              type: string
              required: true
            - name: atlas_url
              in: body
              description: The url of the atlas server
              type: string
              required: true
            - name: atlas_username
              in: body
              description: the username of the atlas user
              type: string
              required: true
            - name: atlas_password
              in: body
              description: the password of the atlas user
              type: string
              required: true
            - name: db_types
              in: body
              description: the db_types from atlas that we want to consider in the matching (i.e. "ted_rdbms_database")
              type: array
              items:
                type: string
              required: true
            - name: matching_algorithm
              in: body
              description: the name of the schema matching algorithm
              type: string
              required: true
            - name: max_number_matches
              in: body
              description: the number of matches that will be given as an output (default 1000)
              type: integer
              required: false
            - name: request_parallelism
              in: body
              description: the number of parallel requests to be made to atlas (default 4)
              type: int
              required: false
            - name: request_chunk_size
              in: body
              description: the number of chunks to request from atlas at once (default 10)
              type: integer
              required: false
            - name: matching_algorithm_params
              in: body
              description: the parameters of the selected matching algorithm (if empty selects defaults)
              type: object
              required: false
        responses:
            200:
                description: Returns the matches
            400:
                description: Invalid guid
            500:
                description: Could not connect to atlas.
    """
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
        r_table: BaseTable = schemata[table.db_belongs_uid].remove_table(table_guid)
        matches = []
        for schema in schemata.values():
            if schema.number_of_columns == 0:
                continue
            matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
            current_schema_matches = matcher.get_matches(schema, table)
            current_schema_matches = sorted(current_schema_matches, key=lambda k: k['sim'],
                                            reverse=True)[:payload.max_number_matches//2]
            matches.extend(current_schema_matches)
        schemata[table.db_belongs_uid].add_table(r_table)
        return format_matches(matches, payload.max_number_matches)


@app.route('/matches/atlas/other_db/<table_guid>/<db_guid>', methods=['GET'])
def find_matches_other_db_atlas(table_guid: str, db_guid: str):
    """ Route that returns the matches of a table from another database in atlas
    ---
    get:
        summary: Endpoint that finds matches in atlas, of a table against the specified database.
        description: Get the matches of a table within atlas with the specified database
        parameters:
            - name: table_guid
              in: path
              description: the guid of the table that we want to find matches
              type: string
              required: true
            - name: db_guid
              in: path
              description: the guid of the database that we want to compare against
              type: string
              required: true
            - name: atlas_url
              in: body
              description: The url of the atlas server
              type: string
              required: true
            - name: atlas_username
              in: body
              description: the username of the atlas user
              type: string
              required: true
            - name: atlas_password
              in: body
              description: the password of the atlas user
              type: string
              required: true
            - name: db_types
              in: body
              description: the db_types from atlas that we want to consider in the matching (i.e. "ted_rdbms_database")
              type: array
              items:
                type: string
              required: true
            - name: matching_algorithm
              in: body
              description: the name of the schema matching algorithm
              type: string
              required: true
            - name: max_number_matches
              in: body
              description: the number of matches that will be given as an output (default 1000)
              type: integer
              required: false
            - name: request_parallelism
              in: body
              description: the number of parallel requests to be made to atlas (default 4)
              type: int
              required: false
            - name: request_chunk_size
              in: body
              description: the number of chunks to request from atlas at once (default 10)
              type: integer
              required: false
            - name: matching_algorithm_params
              in: body
              description: the parameters of the selected matching algorithm (if empty selects defaults)
              type: object
              required: false
        responses:
            200:
                description: Returns the matches
            400:
                description: Invalid guid
            500:
                description: Could not connect to atlas.
    """
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
    """ Route that returns the matches of a table within the database it belongs in atlas
    ---
    get:
        summary: Endpoint that finds matches in atlas, of a table against its own database.
        description: Get the matches of a table within atlas from its own database
        parameters:
            - name: table_guid
              in: path
              description: the guid of the table that we want to find matches
              type: string
              required: true
            - name: atlas_url
              in: body
              description: The url of the atlas server
              type: string
              required: true
            - name: atlas_username
              in: body
              description: the username of the atlas user
              type: string
              required: true
            - name: atlas_password
              in: body
              description: the password of the atlas user
              type: string
              required: true
            - name: db_types
              in: body
              description: the db_types from atlas that we want to consider in the matching (i.e. "ted_rdbms_database")
              type: array
              items:
                type: string
              required: true
            - name: matching_algorithm
              in: body
              description: the name of the schema matching algorithm
              type: string
              required: true
            - name: max_number_matches
              in: body
              description: the number of matches that will be given as an output (default 1000)
              type: integer
              required: false
            - name: request_parallelism
              in: body
              description: the number of parallel requests to be made to atlas (default 4)
              type: int
              required: false
            - name: request_chunk_size
              in: body
              description: the number of chunks to request from atlas at once (default 10)
              type: integer
              required: false
            - name: matching_algorithm_params
              in: body
              description: the parameters of the selected matching algorithm (if empty selects defaults)
              type: object
              required: false
        responses:
            200:
                description: Returns the matches
            400:
                description: Invalid guid
            500:
                description: Could not connect to atlas.
    """
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
    """ Route that returns the holistic matches of a table from the csv store
    ---
    get:
        summary: Endpoint that finds matches in the csv store, of a table against all other tables.
        description: Find matches of a table within the csv store
        parameters:
            - name: table_name
              in: body
              description: name of the table that we want to find its matches
              type: string
              required: true
            - name: db_name
              in: body
              description: the name of the database that the table that we want to find its matches belongs
              type: string
              required: true
            - name: matching_algorithm
              in: body
              description: the name of the schema matching algorithm
              type: string
              required: true
            - name: max_number_matches
              in: body
              description: the number of matches that will be given as an output (default 1000)
              type: integer
              required: false
            - name: matching_algorithm_params
              in: body
              description: the parameters of the selected matching algorithm (if empty selects defaults)
              type: object
              required: false
        responses:
            200:
                description: Returns the matches
            400:
                description: The table does not exist in the csv store
    """
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
        r_table: BaseTable = dbs[table.db_belongs_uid].remove_table(payload.table_name)
        matches = []
        for db in dbs.values():
            if db.number_of_columns == 0:
                continue
            matcher = get_matcher(payload.matching_algorithm, payload.matching_algorithm_params)
            current_schema_matches = matcher.get_matches(db, table)
            current_schema_matches = sorted(current_schema_matches, key=lambda k: k['sim'],
                                            reverse=True)[:payload.max_number_matches//2]
            matches.extend(current_schema_matches)
        dbs[table.db_belongs_uid].add_table(r_table)
        return format_matches(matches, payload.max_number_matches)


@app.route('/matches/csv_store/other_db/<db_name>', methods=['GET'])
def find_matches_other_db_csv(db_name: str):
    """ Route that returns the matches of a table from another database in the csv store
    ---
    get:
        summary: Endpoint that finds matches in the csv store, of a table against a specified database
        description: Find matches of a table within the csv store against the specified database
        parameters:
            - name: db_name
              in: path
              description: the name of the database that we want to compare against
              type: string
              required: true
            - name: table_name
              in: body
              description: name of the table that we want to find its matches
              type: string
              required: true
            - name: db_name
              in: body
              description: the name of the database that the table that we want to find its matches belongs
              type: string
              required: true
            - name: matching_algorithm
              in: body
              description: the name of the schema matching algorithm
              type: string
              required: true
            - name: max_number_matches
              in: body
              description: the number of matches that will be given as an output (default 1000)
              type: integer
              required: false
            - name: matching_algorithm_params
              in: body
              description: the parameters of the selected matching algorithm (if empty selects defaults)
              type: object
              required: false
        responses:
            200:
                description: Returns the matches
            400:
                description: The table does not exist in the csv store
    """
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
    """ Route that returns the matches of a table within the database it belongs in the csv store
    ---
    get:
        summary: Endpoint that finds matches in the csv store, of a table within its own database.
        description: Find matches of a table within the csv store against tables from its own database
        parameters:
            - name: table_name
              in: body
              description: name of the table that we want to find its matches
              type: string
              required: true
            - name: db_name
              in: body
              description: the name of the database that the table that we want to find its matches belongs
              type: string
              required: true
            - name: matching_algorithm
              in: body
              description: the name of the schema matching algorithm
              type: string
              required: true
            - name: max_number_matches
              in: body
              description: the number of matches that will be given as an output (default 1000)
              type: integer
              required: false
            - name: matching_algorithm_params
              in: body
              description: the parameters of the selected matching algorithm (if empty selects defaults)
              type: object
              required: false
        responses:
            200:
                description: Returns the matches
            400:
                description: The table does not exist in the csv store
    """
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
    """ Route that uploads a csv file to the csv store
     ---
     post:
         summary: Endpoint that uploads a csv file in the csv store to the specified database
         description: Upload a csv file in the csv store to the specified database
         parameters:
             - name: db_name
               in: path
               description: the name of the database that we want to put the csv file into
               type: string
               required: true
             - name: file
               in: form
               description: the csv file that we want to upload
               required: true
         responses:
             201:
                 description: File uploaded successfully
             400:
                 description: Wrong or no file
     """
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
    """ Route that uploads an xlsx file to the csv store
     ---
     post:
         summary: Endpoint that uploads an xlsx file to the csv store
         description: Upload an xlsx file to the csv store
         parameters:
             - name: file
               in: form
               description: the xlsx file that we want to upload
               required: true
         responses:
             201:
                 description: File uploaded successfully
             400:
                 description: Wrong or no file
     """
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
    """ Route that shows the layout of the csv store
     ---
     get:
         summary: Endpoint that shows the layout of the csv store
         description: Show the layout of the csv store
         responses:
             200:
                 description: Shows the layout of the csv store
     """
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


if __name__ == '__main__':
    app.run(debug=False)
