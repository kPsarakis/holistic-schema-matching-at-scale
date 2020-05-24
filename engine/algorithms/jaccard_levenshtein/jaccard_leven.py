from itertools import product
from multiprocessing import Pool, get_context
import Levenshtein as Lv

from ..base_matcher import BaseMatcher
from ..match import Match
from ...data_sources.base_column import BaseColumn
from ...data_sources.base_db import BaseDB
from ...data_sources.base_table import BaseTable


class JaccardLevenMatcher(BaseMatcher):
    """
    Class containing the methods for implementing a simple baseline matcher that uses Jaccard Similarity between
    columns to assess their correspondence score, enhanced by Levenshtein Distance.

    Methods
    -------
    jaccard_leven(list1, list2, threshold, process_pool)

    """

    def __init__(self, threshold_leven: float = 0.8, process_num: int = 1):
        """
        Parameters
        ----------
        threshold_leven : float, optional
            The Levenshtein ratio between the two column entries (lower ration, the entries are more different)
        process_num : int, optional
            Te number of processes to spawn
        """
        self.threshold_leven = threshold_leven
        self.process_num = process_num

    def get_matches(self, source: BaseDB, target: BaseDB):
        matches = []
        source_table: BaseTable
        target_table: BaseTable
        source_column: BaseColumn
        target_column: BaseColumn
        for (source_table, target_table) in product(source.get_tables().values(), target.get_tables().values()):
            for source_column, target_column in product(source_table.get_columns(), target_table.get_columns()):
                sim = self.jaccard_leven(source_column.data, target_column.data, self.threshold_leven)
                if sim > 0.0:
                    matches.append(Match(target_table.name, target_table.unique_identifier,
                                         target_column.name, target_column.unique_identifier,
                                         source_table.name, source_table.unique_identifier,
                                         source_column.name, source_column.unique_identifier,
                                         sim).to_dict)
        return matches

    def jaccard_leven(self, list1: list, list2: list, threshold: float) -> float:
        """
        Function that takes two columns and returns their Jaccard similarity based on the Levenshtein ratio between the
        column entries (lower ration, the entries are more different)

        Parameters
        ----------
        list1 : list
            The first column's data
        list2 : list
            The second column's data
        threshold : float
            The Levenshtein ratio

        Returns
        -------
        float
            The Jaccard Levenshtein similarity between the two columns
        """

        if len(set(list1)) < len(set(list2)):
            set1 = set(list1)
            set2 = set(list2)
        else:
            set1 = set(list2)
            set2 = set(list1)

        combinations = list(get_set_combinations(set1, set2, threshold))

        if self.process_num == 1:
            intersection_cnt = 0
            for cmb in combinations:
                intersection_cnt = intersection_cnt + process_lv(cmb)
        else:
            with get_context("spawn").Pool(self.process_num) as process_pool:
                intersection_cnt_list = list(process_pool.map(process_lv, combinations))
                intersection_cnt = sum(intersection_cnt_list)

        union_cnt = len(set1) + len(set2) - intersection_cnt

        if union_cnt == 0:
            return 0

        return float(intersection_cnt) / union_cnt


def get_set_combinations(set1: set, set2: set, threshold: float):
    """
    Function that creates combination between elements of set1 and set2

    Parameters
    ----------
    set1 : set
        The first set that its elements will be taken
    set2 : set
        The second set
    threshold : float
        The Levenshtein ratio

    Returns
    -------
    generator
        A generator that yields one element from the first set, the second set and the Levenshtein ratio
    """
    for s1 in set1:
        yield str(s1), set2, threshold


def process_lv(tup: tuple):
    """
    Function that check if there exist entry from the second set that has a greater Levenshtein ratio with the
    element from the first set than the given threshold

    Parameters
    ----------
    tup : tuple
        A tuple containing one element from the first set, the second set and the threshold of the Levenshtein ratio

    Returns
    -------
    int
        1 if there is such an element 0 if not
    """
    s1, set2, threshold = tup
    for s2 in set2:
        if Lv.ratio(s1, str(s2)) >= threshold:
            return 1
    return 0
