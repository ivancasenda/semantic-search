from tfx.types.component_spec import ChannelParameter
from tfx.types.component_spec import ExecutionParameter
from tfx.types import standard_artifacts
from tfx import types

from artifacts import FeatureVector


INFERENCE_RESULT_KEY = "inference_result"
FEATURE_VECTOR_KEY = "feature_vector"
MATCHING_ENGINE_INDEX_KEY = "update_index"


class MatchingEngineIndexerComponentSpec(types.ComponentSpec):
    """ComponentSpec for MatchingEngineIndexer."""

    PARAMETERS = {
        MATCHING_ENGINE_INDEX_KEY: ExecutionParameter(type=str, optional=True)
    }
    INPUTS = {
        INFERENCE_RESULT_KEY: ChannelParameter(type=standard_artifacts.InferenceResult)
    }
    OUTPUTS = {FEATURE_VECTOR_KEY: ChannelParameter(type=FeatureVector, optional=True)}
