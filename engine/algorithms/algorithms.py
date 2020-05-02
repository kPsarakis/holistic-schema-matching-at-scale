from engine.algorithms.similarity_flooding.similarity_flooding import SimilarityFlooding
from engine.algorithms.cupid.cupid_model import Cupid
from engine.algorithms.coma.coma import Coma
from engine.algorithms.distribution_based.correlation_clustering import CorrelationClustering
from engine.algorithms.jaccard_levenshtein.jaccard_leven import JaccardLevenMatcher

schema_only_algorithms = [SimilarityFlooding.__name__, Cupid.__name__]
instance_only_algorithms = [CorrelationClustering.__name__, JaccardLevenMatcher.__name__]
schema_instance_algorithms = [Coma.__name__]
