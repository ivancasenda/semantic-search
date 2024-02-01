"""MatchingEngineIndexer executor for Vertex AI."""

import os
from typing import Any, Dict, List

from absl import logging
import tensorflow as tf
from tfx import types
from tfx.types import artifact_utils
from tfx.utils import name_utils
from tfx.utils import telemetry_utils

import apache_beam as beam
from tfx.dsl.components.base import base_beam_executor
from tensorflow_serving.apis import prediction_log_pb2
import json

from google.cloud import aiplatform

from pipeline.components.matching_engine_indexer import component_spec


_EMBEDDINGS_FILE_NAME = "embeddings"


@beam.typehints.with_input_types(str)
@beam.typehints.with_output_types(beam.typehints.Iterable[str])
class PredictionLogToJsonlFn(beam.DoFn):
    """Create serialized json containing id and embedding
    from PredictionLog outputs"""

    def process(self, element, *args, **kwargs):
        del args, kwargs

        ids = tf.make_ndarray(element.predict_log.response.outputs["id"])
        embeddings = tf.make_ndarray(element.predict_log.response.outputs["embedding"])

        for id, embedding in zip(ids, embeddings):
            feature_vector_json = json.dumps(
                {"id": str(int(id)), "embedding": [str(value) for value in embedding]}
            )
            yield feature_vector_json


class Executor(base_beam_executor.BaseBeamExecutor):
    """MatchingEngineIndexer executor to create or update
    Matching Engine Index on Vertex AI."""

    def Do(
        self,
        input_dict: Dict[str, List[types.Artifact]],
        output_dict: Dict[str, List[types.Artifact]],
        exec_properties: Dict[str, Any],
    ) -> None:
        """Runs batch inference on a given model with given input examples.

        This function creates a new index (if necessary) and a new model version
        before inference, and cleans up resources after inference. It provides
        re-executability as it cleans up (only) the model resources that are created
        during the process even inference job failed.

        Args:
          input_dict: Input dict from input key to a list of Artifacts.
            - examples: examples for inference.
            - model: exported model.
            - model_blessing: model blessing result
          output_dict: Output dict from output key to a list of Artifacts.
            - output: bulk inference results.
          exec_properties: A dict of execution properties.
            - data_spec: JSON string of bulk_inferrer_pb2.DataSpec instance.
            - custom_config: custom_config.ai_platform_serving_args need to contain
              the serving job parameters sent to Google Cloud Vertex AI. For the
              full set of parameters, refer to
              https://googleapis.dev/python/aiplatform/latest/aiplatform.html?highlight=deploy#google.cloud.aiplatform.Model.deploy

        Returns:
          None
        """
        self._log_startup(input_dict, output_dict, exec_properties)

        if component_spec.INFERENCE_RESULT_KEY not in input_dict:
            raise ValueError(
                "{} is missing in input dict.".format(
                    component_spec.INFERENCE_RESULT_KEY
                )
            )

        if component_spec.MATCHING_ENGINE_INDEX_KEY not in exec_properties:
            raise ValueError("Need resource name of matching engine index!")

        executor_class_path = name_utils.get_full_name(self.__class__)
        with telemetry_utils.scoped_labels(
            {telemetry_utils.LABEL_TFX_EXECUTOR: executor_class_path}
        ):
            job_labels = telemetry_utils.make_labels_dict()

        inference_result_uri = artifact_utils.get_single_uri(
            input_dict[component_spec.INFERENCE_RESULT_KEY]
        )
        prediction_log_path = f"{inference_result_uri}/*.gz"

        logging.info("Input inference result will be read from ", prediction_log_path)

        prediction_log_decoder = beam.coders.ProtoCoder(
            prediction_log_pb2.PredictionLog
        )

        feature_vector = artifact_utils.get_single_instance(
            output_dict[component_spec.FEATURE_VECTOR_KEY]
        )

        logging.info("Executing beam pipeline")

        with self._make_beam_pipeline() as pipeline:
            _ = (
                pipeline
                | "Read Prediction Log"
                >> beam.io.ReadFromTFRecord(
                    prediction_log_path, coder=prediction_log_decoder
                )
                | "Create Serialized JSON id, embedding"
                >> beam.ParDo(PredictionLogToJsonlFn())
                | "Write JSON file to GCS"
                >> beam.io.WriteToText(
                    file_path_prefix=os.path.join(
                        feature_vector.uri, _EMBEDDINGS_FILE_NAME
                    ),
                    file_name_suffix=".json",
                )
            )

        logging.info("Finished executing pipeline")

        resource_name = exec_properties.get(component_spec.MATCHING_ENGINE_INDEX_KEY)

        if not resource_name:
            logging.info(
                "GCP matching engine index resource name not found, will not perform update on index"
            )
            return

        matching_engine_index = aiplatform.MatchingEngineIndex(resource_name)

        logging.info("Updating index embeddings on gcp resource ", resource_name)

        matching_engine_index.update_embeddings(contents_delta_uri=feature_vector.uri)
