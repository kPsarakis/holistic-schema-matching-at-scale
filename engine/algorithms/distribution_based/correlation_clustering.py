import json
from multiprocessing import Pool, get_context
from itertools import combinations
from typing import List

from . import discovery
from .clustering_utils import create_cache_dirs, generate_global_ranks, process_columns, ingestion_column_generator, \
    process_emd
from ..base_matcher import BaseMatcher
from ..match import Match
from ...data_sources.base_column import BaseColumn
from ...data_sources.base_db import BaseDB
from ...data_sources.base_table import BaseTable
from ...utils.utils import get_project_root


class CorrelationClustering(BaseMatcher):
    """
    A class that contains the data and methods required for the algorithms proposed in
    "Automatic Discovery of Attributes in Relational Databases" from M. Zhang et al. [1]

    Attributes
    ----------
    threshold1: float
        The threshold for phase 1
    threshold2: float
        The threshold for phase 2
    quantiles: int
        the number of quantiles of the histograms
    process_num: int
        The number of processes to spawn
    chunk_size: int, optional
        The size of each chunk to process
    clear_cache: bool, optional
        Clear cached files or not
    column_names: list
        List containing all the column names
    dataset_name: str
        The name of the dataset

    Methods
    -------
    find_matches(pool, chunk_size)
         A dictionary with matches and their similarity

    rank_output(attribute_clusters)
        Take the attribute clusters that the algorithm produces and give a ranked list of matches based on the the EMD
        between each pair inside an attribute cluster

    """

    def __init__(self, threshold1: float = 0.15, threshold2: float = 0.15,
                 quantiles: int = 256, process_num: int = 1, chunk_size: int = None, clear_cache: bool = True):
        """
        Parameters
        ----------
        threshold1: float
            The threshold for phase 1
        threshold2: float
            The threshold for phase 2
        quantiles: int
            the number of quantiles of the histograms
        process_num: int
            The number of processes to spawn
        chunk_size: int, optional
            The size of each chunk to process
        clear_cache: bool, optional
            Clear cached files or not
        """
        self.quantiles = quantiles
        self.threshold1 = threshold1
        self.threshold2 = threshold2
        self.process_num = process_num
        self.chunk_size = chunk_size
        self.clear_cache = clear_cache
        self.column_names = []
        self.dataset_name = None
        self.target_name = None
        create_cache_dirs()

    def get_matches(self, source: BaseDB, target: BaseDB):
        """
        Overridden function of the BaseMatcher tha gets the source, the target data loaders and the dataset name.
        Next it gives as an output a ranked list of column pair matches.

        Parameters
        ----------
        source: InstanceLoader
            The source dataset
        target: InstanceLoader
            The target dataset

        Returns
        -------
        dict
            A dictionary with matches and their similarity
        """
        self.target_name = target.name
        self.dataset_name = source.name + "___" + target.name
        all_tables: List[BaseTable] = list(source.get_tables().values()) + list(target.get_tables().values())

        if self.clear_cache:
            data = []
            for table in all_tables:
                for column in table.get_columns():
                    data.extend(column.data)
            generate_global_ranks(data, self.dataset_name)
            del data

        with get_context("spawn").Pool(self.process_num) as process_pool:
            for table in all_tables:
                self.column_names.extend(list(map(lambda x: (table.name, table.unique_identifier,
                                                             x.name, x.unique_identifier),
                                                  table.get_columns())))
                columns: List[BaseColumn] = table.get_columns()
                process_pool.map(process_columns, ingestion_column_generator(columns, table.name,
                                                                             str(table.unique_identifier),
                                                                             self.dataset_name, self.quantiles))

            matches = self.find_matches(process_pool, self.chunk_size)

        return matches

    def find_matches(self, pool: Pool, chunk_size: int = None):
        """
        "Main" function of [1] that will calculate first the distribution clusters and then the attribute clusters

        Parameters
        ---------
        pool: multiprocessing.Pool
            the process pool that will be used in the algorithms 1, 2 and 3 of [1]
        chunk_size: int, optional
            the number of chunks of each job process (default let the framework decide)
        """
        connected_components = discovery.compute_distribution_clusters(self.column_names, self.dataset_name,
                                                                       self.threshold1, pool, chunk_size,
                                                                       self.quantiles)

        # self.write_clusters_to_json(connected_components, 'Distribution_Clusters.json')

        all_attributes = list()
        i = 1
        for components in connected_components:
            if len(components) > 1:
                i = i + 1
                edges = discovery.compute_attributes(list(components), self.dataset_name, self.threshold2, pool,
                                                     chunk_size, self.quantiles)
                all_attributes.append((list(components), edges))

        results = list()
        for components, edges in all_attributes:
            results.append(discovery.correlation_clustering_pulp(components, edges))

        attribute_clusters = discovery.process_correlation_clustering_result(results, self.column_names)

        # self.write_clusters_to_json(attribute_clusters, 'Attribute_Clusters(Matches).json')

        return self.rank_output(attribute_clusters)

    @staticmethod
    def write_clusters_to_json(clusters: list, file_name: str):
        """
        Writes the clusters with their attributes and their connections in a json file

        Parameters
        ---------
        clusters : list(list(str))
            a list with the clusters, their attributes and their connections
        file_name : str
            the name of the JSON file to write
        """
        d = {}
        clusters.sort(key=lambda item: -len(item))
        for (cluster, idx) in zip(clusters, range(len(clusters))):
            d["Cluster " + str(idx + 1)] = {}
            table_names = list(map(lambda x: x[0], cluster))
            for table_name in table_names:
                column_names = map(lambda x: x[1], filter(lambda x: x[0] == table_name, cluster))
                d["Cluster " + str(idx + 1)][table_name] = list(column_names)
        with open(get_project_root() + "/" + file_name, 'w') as fp:
            json.dump(d, fp, indent=2)

    def rank_output(self, attribute_clusters: iter):
        """
        Take the attribute clusters that the algorithm produces and give a ranked list of matches based on the the EMD
        between each pair inside an attribute cluster . The ranked list will look like:
        ((table_name1, column_name1), (table_name2, column_name2)): similarity

        Parameters
        ----------
        attribute_clusters: list
            The attribute clusters
        Returns
        -------
        dict
            A ranked list that will look like: ((table_name1, column_name1), (table_name2, column_name2)): similarity
        """
        matches = []
        for cluster in attribute_clusters:
            if len(cluster) > 1:
                for combination in combinations(cluster, 2):
                    table1 = combination[0][0]
                    table2 = combination[1][0]
                    if table1 != table2:
                        k, emd = process_emd(((combination[0], combination[1]),
                                              self.dataset_name, self.quantiles, False))
                        sim = 1 / (1 + emd)
                        tn_i, tguid_i, cn_i, cguid_i = k[0]
                        tn_j, tguid_j, cn_j, cguid_j = k[1]
                        if self.target_name == tn_i:
                            matches.append(Match(tn_i, tguid_i, cn_i, cguid_i, tn_j, tguid_j, cn_j, cguid_j, sim)
                                           .to_dict)
                        else:
                            matches.append(Match(tn_j, tguid_j, cn_j, cguid_j, tn_i, tguid_i, cn_i, cguid_i, sim)
                                           .to_dict)
        return matches
