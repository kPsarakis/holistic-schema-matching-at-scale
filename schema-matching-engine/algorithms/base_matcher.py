from abc import ABC, abstractmethod
from typing import List, Dict

from data_sources.base_db import BaseDB


class BaseMatcher(ABC):

    @abstractmethod
    def get_matches(self, source_input: BaseDB, target_input: BaseDB) -> List[Dict]:
        """
        Get the column matches from a schema matching algorithm
        :returns List of matches
        """
        raise NotImplementedError
