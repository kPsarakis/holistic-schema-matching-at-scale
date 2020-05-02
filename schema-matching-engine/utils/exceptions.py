from flask import abort

from data_sources.base_db import BaseDB
from data_sources.base_table import BaseTable


def check_if_table_has_columns(table: BaseTable):
    if table.number_of_columns == 0:
        abort(400, "The given table does not contain any columns")


def check_if_db_is_empty(db: BaseDB):
    if len(db.get_tables()) == 0:
        abort(400, "The database does not contain any tables with columns")
