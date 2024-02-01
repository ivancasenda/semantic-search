"""MatchingEngineIndexer component for Vertex AI."""

from typing import Union, Optional

from tfx import types
from tfx.dsl.components.base import base_beam_component
from tfx.dsl.components.base import executor_spec
from tfx.orchestration.data_types import RuntimeParameter

from pipeline.components.matching_engine_indexer import executor, component_spec


class MatchingEngineIndexerComponent(base_beam_component.BaseBeamComponent):
    """A Vertex AI component to Create or update index for matching engine.

    Component will consume the inference results PredictionLog proto from BulkInferrer
    produces JSONL data as input to create or update Matching Engine Index, and deploy
    index to Matching Engine Endpoint.

    Component `outputs` contains:
    - `inference_result`: Channel of type `standard_artifacts.InferenceResult`
                            to store the inference results.
    """

    SPEC_CLASS = component_spec.MatchingEngineIndexerComponentSpec
    EXECUTOR_SPEC = executor_spec.BeamExecutorSpec(executor.Executor)

    def __init__(
        self,
        inference_result: types.Channel,
        update_index: Optional[Union[str, RuntimeParameter]],
    ):
        """Construct an BulkInferrer component.

        Args:
        inference_results: A Channel of type `standard_artifacts.InferenceResult`, usually
            produced by an BulkInferrer component. _required_
        update_index: Resource name for matching engine index (Ex: projects/106169385731/locations/asia-southeast1/indexes/38931507716292608)
        custom_config: A dict which contains the deployment job parameters to be
            passed to Google Cloud Vertex AI.
            custom_config.ai_platform_serving_args need to contain the serving job
            parameters. For the full set of parameters, refer to
            https://googleapis.dev/python/aiplatform/latest/aiplatform.html?highlight=deploy#google.cloud.aiplatform.Model.deploy
        """
        feature_vector = types.Channel(type=component_spec.FeatureVector)

        spec = component_spec.MatchingEngineIndexerComponentSpec(
            inference_result=inference_result,
            update_index=update_index,
            feature_vector=feature_vector,
        )
        super().__init__(spec=spec)
