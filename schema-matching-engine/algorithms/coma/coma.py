import shutil
import subprocess
import os
import csv

from itertools import product
from typing import List, Dict
from algorithms.base_matcher import BaseMatcher
from algorithms.match import Match
from data_sources.base_db import BaseDB
from data_sources.base_table import BaseTable
from utils.utils import get_project_root, create_folder


class Coma(BaseMatcher):

    def __init__(self, max_n: int = 0, strategy: str = "COMA_OPT"):
        self.max_n = max_n
        self.strategy = strategy

    def get_matches(self, source_input: BaseDB, target_input: BaseDB) -> List[Dict]:
        create_folder(get_project_root() + '/algorithms/coma/tmp_data')
        create_folder(get_project_root() + '/algorithms/coma/coma_output')
        dataset_name = source_input.name + "____" + target_input.name
        coma_output_path = get_project_root() + "/algorithms/coma/coma_output/" + dataset_name + str(self.max_n) + \
                           self.strategy + ".txt"

        matches = []

        source_tables = [table for table in source_input.get_tables().values()]
        target_tables = [table for table in target_input.get_tables().values()]

        for s_table, t_table in product(source_tables, target_tables):
            s_fname, t_fname = self.write_schema_csv_files(s_table, t_table)
            self.run_coma_jar(s_fname, t_fname, coma_output_path)
            raw_output = self.read_coma_output(coma_output_path)
            matches.extend(self.process_coma_output(raw_output, t_table, s_table))

        os.remove(coma_output_path)
        shutil.rmtree(get_project_root() + '/algorithms/coma/tmp_data')

        return matches

    def run_coma_jar(self, source_table_fname: str, target_table_fname: str, coma_output_path):
        jar_path = get_project_root() + '/algorithms/coma/artifact/coma.jar'
        jar_path = os.path.relpath(jar_path, get_project_root())
        source_data = os.path.relpath(source_table_fname, get_project_root())
        target_data = os.path.relpath(target_table_fname, get_project_root())
        coma_output_path = os.path.relpath(coma_output_path, get_project_root())
        fh = open("NUL", "w")
        subprocess.call(['java', '-Xmx2000m',  # YOU MIGHT NEED TO INCREASE THE MEMORY HERE WITH BIGGER TABLES
                         '-cp', jar_path,
                         '-DinputFile1=' + source_data,
                         '-DinputFile2=' + target_data,
                         '-DoutputFile=' + coma_output_path,
                         '-DmaxN=' + str(self.max_n),
                         '-Dstrategy=' + self.strategy,
                         'Main'], stdout=fh, stderr=fh)

    def write_schema_csv_files(self, table1: BaseTable, table2: BaseTable):
        fname1 = self.write_csv_file(table1.name, list(map(lambda x: x.name, table1.get_columns())))
        fname2 = self.write_csv_file(table2.name, list(map(lambda x: x.name, table2.get_columns())))
        return fname1, fname2

    def process_coma_output(self, matches, t_table: BaseTable, s_table: BaseTable) -> List:
        formatted_output = []
        t_lookup = t_table.get_guid_column_lookup
        s_lookup = s_table.get_guid_column_lookup
        for match in matches:
            m, similarity = match.split(":")
            m1, m2 = m.split(" <-> ")
            column1 = self.get_column(m2)
            column2 = self.get_column(m1)
            if column1 == "" or column2 == "":
                continue
            formatted_output.append(Match(t_table.name, t_table.unique_identifier, column1, t_lookup[column1],
                                          s_table.name, s_table.unique_identifier, column2, s_lookup[column2],
                                          float(similarity)).to_dict)
        return formatted_output

    @staticmethod
    def write_csv_file(table_name: str, data: List[str]) -> str:
        fname: str = get_project_root() + '/algorithms/coma/tmp_data/' + table_name + '.csv'
        with open(fname, 'w', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(data)
        return fname

    @staticmethod
    def read_coma_output(coma_output_path):
        with open(coma_output_path) as f:
            matches = f.readlines()
        matches = [x.strip() for x in matches]
        matches.pop()
        return matches

    @staticmethod
    def get_column(match) -> str:
        return ".".join(match.split(".")[1:])
