"""BulkInferrer component for Vertex AI."""

from typing import Any, Dict, Optional, Union

from tfx import types
from tfx.dsl.components.base import base_beam_component
from tfx.dsl.components.base import executor_spec
from tfx.orchestration import data_types
from tfx.proto import bulk_inferrer_pb2
from tfx.types import standard_artifacts
from tfx.types.component_spec import ChannelParameter
from tfx.types.component_spec import ExecutionParameter
from tfx.utils import json_utils

from pipeline.components.vertex_ai_bulk_inferrer import executor


class VertexAIBulkInferrerComponentSpec(types.ComponentSpec):
    """ComponentSpec for BulkInferrer component of Vertex AI."""

    PARAMETERS = {
        "data_spec": ExecutionParameter(type=bulk_inferrer_pb2.DataSpec, optional=True),
        "output_example_spec": ExecutionParameter(
            type=bulk_inferrer_pb2.OutputExampleSpec, optional=True
        ),
        "custom_config": ExecutionParameter(type=str),
    }
    INPUTS = {
        "examples": ChannelParameter(type=standard_artifacts.Examples),
        "model": ChannelParameter(type=standard_artifacts.Model),
        "model_blessing": ChannelParameter(
            type=standard_artifacts.ModelBlessing, optional=True
        ),
    }
    OUTPUTS = {
        "inference_result": ChannelParameter(
            type=standard_artifacts.InferenceResult, optional=True
        ),
        "output_examples": ChannelParameter(
            type=standard_artifacts.Examples, optional=True
        ),
    }


class VertexAIBulkInferrerComponent(base_beam_component.BaseBeamComponent):
    """A Vertex AI component to do batch inference on a remote hosted model.

    BulkInferrer component will push a model to Google Cloud Vertex AI,
    consume examples data, send request to the remote hosted model,
    and produces the inference results to an external location
    as PredictionLog proto. After inference, it will delete the model from
    Google Cloud Vertex AI.

    Component `outputs` contains:
    - `inference_result`: Channel of type `standard_artifacts.InferenceResult`
                            to store the inference results.
    - `output_examples`: Channel of type `standard_artifacts.Examples`
                            to store the output examples.
    """

    SPEC_CLASS = VertexAIBulkInferrerComponentSpec
    EXECUTOR_SPEC = executor_spec.BeamExecutorSpec(executor.Executor)

    def __init__(
        self,
        examples: types.Channel,
        model: Optional[types.Channel] = None,
        model_blessing: Optional[types.Channel] = None,
        data_spec: Optional[
            Union[bulk_inferrer_pb2.DataSpec, data_types.RuntimeParameter]
        ] = None,
        output_example_spec: Optional[
            Union[bulk_inferrer_pb2.OutputExampleSpec, data_types.RuntimeParameter]
        ] = None,
        custom_config: Optional[Dict[str, Any]] = None,
    ):
        """Construct an BulkInferrer component.

        Args:
        examples: A Channel of type `standard_artifacts.Examples`, usually
            produced by an ExampleGen component. _required_
        model: A Channel of type `standard_artifacts.Model`, usually produced by
            a Trainer component.
        model_blessing: A Channel of type `standard_artifacts.ModelBlessing`,
            usually produced by a ModelValidator component.
        data_spec: bulk_inferrer_pb2.DataSpec instance that describes data
            selection.
        output_example_spec: bulk_inferrer_pb2.OutputExampleSpec instance, specify
            if you want BulkInferrer to output examples instead of inference result.
        custom_config: A dict which contains the deployment job parameters to be
            passed to Google Cloud Vertex AI.
            custom_config.ai_platform_serving_args need to contain the serving job
            parameters. For the full set of parameters, refer to
            https://googleapis.dev/python/aiplatform/latest/aiplatform.html?highlight=deploy#google.cloud.aiplatform.Model.deploy

        Raises:
        ValueError: Must not specify inference_result or output_examples depends
            on whether output_example_spec is set or not.
        """
        if output_example_spec:
            output_examples = types.Channel(type=standard_artifacts.Examples)
            inference_result = None
        else:
            inference_result = types.Channel(type=standard_artifacts.InferenceResult)
            output_examples = None

        spec = VertexAIBulkInferrerComponentSpec(
            examples=examples,
            model=model,
            model_blessing=model_blessing,
            data_spec=data_spec or bulk_inferrer_pb2.DataSpec(),
            output_example_spec=output_example_spec,
            custom_config=json_utils.dumps(custom_config),
            inference_result=inference_result,
            output_examples=output_examples,
        )
        super().__init__(spec=spec)
