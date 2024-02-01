"""BulkInferrer executor for Vertex AI."""

import hashlib
import importlib
import os
from typing import Any, Callable, Dict, List, Optional, Union

from absl import logging
import apache_beam as beam
import tensorflow as tf
from tfx import types
from tfx.components.bulk_inferrer import prediction_to_example_utils
from tfx.components.util import model_utils
from tfx.components.util import tfxio_utils
from tfx.dsl.components.base import base_beam_executor
from tfx.proto import bulk_inferrer_pb2
from tfx.proto import example_gen_pb2
from tfx.types import artifact_utils
from tfx.utils import io_utils
from tfx.utils import path_utils
from tfx.utils import proto_utils
from tfx.utils import json_utils
from tfx.utils import name_utils
from tfx.utils import telemetry_utils
from tfx_bsl.tfxio import record_based_tfxio

from pipeline.components.vertex_ai_bulk_inferrer.public.proto import model_spec_pb2
from pipeline.components.vertex_ai_bulk_inferrer.public.beam import run_inference
from pipeline.components.vertex_ai_bulk_inferrer import runner, constants

from tensorflow_serving.apis import prediction_log_pb2

# Workarounds for importing extra dependencies. Do not add more.
for name in ["tensorflow_text", "tensorflow_recommenders"]:
    try:
        importlib.import_module(name)
    except ImportError:
        logging.info("%s is not available.", name)

from tensorflow.python.saved_model import (
    loader_impl,
)  # pylint:disable=g-direct-tensorflow-import

# We define the following aliases of Any because the actual types are not
# public.
_SignatureDef = Any

# Keys for custom_config.
_CUSTOM_CONFIG_KEY = "custom_config"
_PREDICTION_LOGS_FILE_NAME = "prediction_logs"
_EXAMPLES_FILE_NAME = "examples"
_TELEMETRY_DESCRIPTORS = ["VertexAIBulkInferrer"]


class Executor(base_beam_executor.BaseBeamExecutor):
    """Bulk inferer executor for inference on AI Platform."""

    def Do(
        self,
        input_dict: Dict[str, List[types.Artifact]],
        output_dict: Dict[str, List[types.Artifact]],
        exec_properties: Dict[str, Any],
    ) -> None:
        """Runs batch inference on a given model with given input examples.

        This function creates a new model (if necessary) and a new model version
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

        if output_dict.get("inference_result"):
            inference_result = artifact_utils.get_single_instance(
                output_dict["inference_result"]
            )
        else:
            inference_result = None
        if output_dict.get("output_examples"):
            output_examples = artifact_utils.get_single_instance(
                output_dict["output_examples"]
            )
        else:
            output_examples = None

        if "examples" not in input_dict:
            raise ValueError("`examples` is missing in input dict.")
        if "model" not in input_dict:
            raise ValueError(
                "Input models are not valid, model " "need to be specified."
            )
        if "model_blessing" in input_dict:
            model_blessing = artifact_utils.get_single_instance(
                input_dict["model_blessing"]
            )
            if not model_utils.is_model_blessed(model_blessing):
                logging.info("Model on %s was not blessed ", model_blessing.uri)
                return
        else:
            logging.info("Model blessing is not provided, exported model will be used.")

        if _CUSTOM_CONFIG_KEY not in exec_properties:
            raise ValueError(
                "Input exec properties are not valid, {} "
                "need to be specified.".format(_CUSTOM_CONFIG_KEY)
            )

        custom_config = json_utils.loads(
            exec_properties.get(_CUSTOM_CONFIG_KEY, "null")
        )
        if custom_config is not None and not isinstance(custom_config, Dict):
            raise ValueError(
                "custom_config in execution properties needs to be a " "dict."
            )
        ai_platform_serving_args = custom_config.get(constants.SERVING_ARGS_KEY)
        if not ai_platform_serving_args:
            raise ValueError("`ai_platform_serving_args` is missing in `custom_config`")

        batch_parameters_args = custom_config.get(constants.BATCH_PARAMETERS_ARGS_KEY)

        executor_class_path = name_utils.get_full_name(self.__class__)
        with telemetry_utils.scoped_labels(
            {telemetry_utils.LABEL_TFX_EXECUTOR: executor_class_path}
        ):
            job_labels = telemetry_utils.make_labels_dict()
        model = artifact_utils.get_single_instance(input_dict["model"])
        model_path = path_utils.serving_model_path(
            model.uri, path_utils.is_old_model_artifact(model)
        )
        logging.info("Use exported model from %s.", model_path)
        # Use model artifact uri to generate model version to guarantee the
        # 1:1 mapping from model version to model.
        model_version = "version_" + hashlib.sha256(model.uri.encode()).hexdigest()

        inference_spec = self._get_inference_spec(
            model_path, model_version, ai_platform_serving_args, batch_parameters_args
        )

        data_spec = bulk_inferrer_pb2.DataSpec()
        proto_utils.json_to_proto(exec_properties["data_spec"], data_spec)
        output_example_spec = bulk_inferrer_pb2.OutputExampleSpec()
        if exec_properties.get("output_example_spec"):
            proto_utils.json_to_proto(
                exec_properties["output_example_spec"], output_example_spec
            )
        endpoint_region = custom_config.get(constants.VERTEX_REGION_KEY)
        if not endpoint_region:
            raise ValueError(
                "`{}` is missing in `custom_config`".format(constants.VERTEX_REGION_KEY)
            )

        serving_container_image_uri = custom_config.get(
            constants.VERTEX_CONTAINER_IMAGE_URI_KEY
        )
        if not serving_container_image_uri:
            raise ValueError(
                "`{}` is missing in `custom_config`".format(
                    constants.VERTEX_CONTAINER_IMAGE_URI_KEY
                )
            )

        new_model_created = False
        try:
            new_model_created = runner.deploy_model_for_aip_prediction(
                serving_path=model_path,
                model_version_name=model_version,
                ai_platform_serving_args=ai_platform_serving_args,
                labels=job_labels,
                serving_container_image_uri=serving_container_image_uri,
                endpoint_region=endpoint_region,
                skip_model_endpoint_creation=False,
                enable_vertex=True,
            )
            self._run_model_inference(
                data_spec,
                output_example_spec,
                input_dict["examples"],
                output_examples,
                inference_result,
                inference_spec,
            )
        except Exception as e:
            logging.error(
                "Error in executing VertexAIBulkInferrerComponent: %s", str(e)
            )
            raise
        finally:
            # Guarantee newly created resources are cleaned up even if the inference
            # job failed.

            # Clean up the newly deployed model.
            runner.delete_model_from_aip_if_exists(
                model_version_name=model_version,
                ai_platform_serving_args=ai_platform_serving_args,
                delete_model_endpoint=new_model_created,
                enable_vertex=True,
            )

    def _get_inference_spec(
        self,
        model_path: str,
        model_version: str,
        ai_platform_serving_args: Dict[str, Any],
        batch_parameters_args: Dict[str, Any],
    ) -> model_spec_pb2.InferenceSpecType:
        if "project_id" not in ai_platform_serving_args:
            raise ValueError("`project_id` is missing in `ai_platform_serving_args`")
        project_id = ai_platform_serving_args["project_id"]

        endpoint_name = ai_platform_serving_args["endpoint_name"]

        vertex_ai_prediction_model_spec = model_spec_pb2.VertexAIPredictionModelSpec(
            project_id=project_id, model_name=model_version
        )
        model_signature = self._get_model_signature(model_path)
        if (
            len(model_signature.inputs) == 1
            and list(model_signature.inputs.values())[0].dtype
            == tf.string.as_datatype_enum
        ):
            vertex_ai_prediction_model_spec.use_serialization_config = True

        logging.info(
            "Using hosted model on Vertex AI platform, endpoint_name: %s,"
            "model_version: %s.",
            endpoint_name,
            model_version,
        )

        batch_parameters = model_spec_pb2.BatchParameters(**batch_parameters_args)

        logging.info("Using Batch Parameters: %s", str(batch_parameters_args))

        result = model_spec_pb2.InferenceSpecType()
        result.vertex_ai_prediction_model_spec.CopyFrom(vertex_ai_prediction_model_spec)
        result.batch_parameters.CopyFrom(batch_parameters)
        return result

    def _get_model_signature(self, model_path: str) -> _SignatureDef:
        """Returns a model signature."""

        saved_model_pb = loader_impl.parse_saved_model(model_path)
        meta_graph_def = None
        for graph_def in saved_model_pb.meta_graphs:
            if graph_def.meta_info_def.tags == [
                tf.compat.v1.saved_model.tag_constants.SERVING
            ]:
                meta_graph_def = graph_def
        if not meta_graph_def:
            raise RuntimeError(
                "Tag tf.compat.v1.saved_model.tag_constants.SERVING"
                " does not exist in saved model: %s. This is required"
                " for remote inference." % model_path
            )
        if tf.saved_model.PREDICT_METHOD_NAME in meta_graph_def.signature_def:
            return meta_graph_def.signature_def[tf.saved_model.PREDICT_METHOD_NAME]
        if (
            tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
            in meta_graph_def.signature_def
        ):
            return meta_graph_def.signature_def[
                tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
            ]
        raise RuntimeError(
            "Cannot find serving signature in saved model: %s,"
            " tf.saved_model.PREDICT_METHOD_NAME or "
            " tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY is needed." % model_path
        )

    def _run_model_inference(
        self,
        data_spec: bulk_inferrer_pb2.DataSpec,
        output_example_spec: bulk_inferrer_pb2.OutputExampleSpec,
        examples: List[types.Artifact],
        output_examples: Optional[types.Artifact],
        inference_result: Optional[types.Artifact],
        inference_endpoint: model_spec_pb2.InferenceSpecType,
    ) -> None:
        """Runs model inference on given examples data.

        Args:
        data_spec: bulk_inferrer_pb2.DataSpec instance.
        output_example_spec: bulk_inferrer_pb2.OutputExampleSpec instance.
        examples: List of `standard_artifacts.Examples` artifacts.
        output_examples: Optional output `standard_artifacts.Examples` artifact.
        inference_result: Optional output `standard_artifacts.InferenceResult`
            artifact.
        inference_endpoint: Model inference endpoint.
        """

        example_uris = {}
        for example_artifact in examples:
            for split in artifact_utils.decode_split_names(
                example_artifact.split_names
            ):
                if data_spec.example_splits:
                    if split in data_spec.example_splits:
                        example_uris[split] = artifact_utils.get_split_uri(
                            [example_artifact], split
                        )
                else:
                    example_uris[split] = artifact_utils.get_split_uri(
                        [example_artifact], split
                    )

        payload_format, _ = tfxio_utils.resolve_payload_format_and_data_view_uri(
            examples
        )

        tfxio_factory = tfxio_utils.get_tfxio_factory_from_artifact(
            examples,
            _TELEMETRY_DESCRIPTORS,
            schema=None,
            read_as_raw_records=True,
            # We have to specify this parameter in order to create a RawRecord TFXIO
            # but we won't use the RecordBatches so the column name of the raw
            # records does not matter.
            raw_record_column_name="unused",
        )

        if output_examples:
            output_examples.split_names = artifact_utils.encode_split_names(
                sorted(example_uris.keys())
            )

        with self._make_beam_pipeline() as pipeline:
            data_list = []
            for split, example_uri in example_uris.items():
                tfxio = tfxio_factory([io_utils.all_files_pattern(example_uri)])
                assert isinstance(
                    tfxio, record_based_tfxio.RecordBasedTFXIO
                ), "Unable to use TFXIO {} as it does not support reading raw records.".format(
                    type(tfxio)
                )
                # pylint: disable=no-value-for-parameter
                data = (
                    pipeline
                    | "ReadData[{}]".format(split) >> tfxio.RawRecordBeamSource()
                    | "RunInference[{}]".format(split)
                    >> _RunInference(payload_format, inference_endpoint)
                )
                if output_examples:
                    output_examples_split_uri = artifact_utils.get_split_uri(
                        [output_examples], split
                    )
                    logging.info(
                        "Path of output examples split `%s` is %s.",
                        split,
                        output_examples_split_uri,
                    )
                    _ = data | "WriteExamples[{}]".format(split) >> _WriteExamples(
                        output_example_spec, output_examples_split_uri
                    )
                    # pylint: enable=no-value-for-parameter

                data_list.append(data)

            if inference_result:
                _ = (
                    data_list
                    | "FlattenInferenceResult" >> beam.Flatten(pipeline=pipeline)
                    | "WritePredictionLogs"
                    >> beam.io.WriteToTFRecord(
                        os.path.join(inference_result.uri, _PREDICTION_LOGS_FILE_NAME),
                        file_name_suffix=".gz",
                        coder=beam.coders.ProtoCoder(prediction_log_pb2.PredictionLog),
                    )
                )

        if output_examples:
            logging.info("Output examples written to %s.", output_examples.uri)
        if inference_result:
            logging.info("Inference result written to %s.", inference_result.uri)


def _MakeParseFn(
    payload_format: int,
) -> Union[
    Callable[[bytes], tf.train.Example], Callable[[bytes], tf.train.SequenceExample]
]:
    """Returns a function to parse bytes to payload."""
    if payload_format == example_gen_pb2.PayloadFormat.FORMAT_TF_EXAMPLE:
        return tf.train.Example.FromString
    elif payload_format == example_gen_pb2.PayloadFormat.FORMAT_TF_SEQUENCE_EXAMPLE:
        return tf.train.SequenceExample.FromString
    else:
        raise NotImplementedError(
            "Payload format %s is not supported."
            % example_gen_pb2.PayloadFormat.Name(payload_format)
        )


@beam.ptransform_fn
@beam.typehints.with_output_types(prediction_log_pb2.PredictionLog)
def _RunInference(
    pipeline: beam.pvalue.PCollection,
    payload_format: int,
    inference_endpoint: model_spec_pb2.InferenceSpecType,
) -> beam.pvalue.PCollection:
    """Runs model inference on given examples data."""
    return (
        pipeline
        | "ParseExamples" >> beam.Map(_MakeParseFn(payload_format))
        | "RunInference" >> run_inference.RunInference(inference_endpoint)
    )


@beam.ptransform_fn
@beam.typehints.with_input_types(prediction_log_pb2.PredictionLog)
def _WriteExamples(
    prediction_log: beam.pvalue.PCollection,
    output_example_spec: bulk_inferrer_pb2.OutputExampleSpec,
    output_path: str,
) -> beam.pvalue.PDone:
    """Converts `prediction_log` to `tf.train.Example` and materializes."""
    return (
        prediction_log
        | "ConvertToExamples"
        >> beam.Map(
            prediction_to_example_utils.convert, output_example_spec=output_example_spec
        )
        | "WriteExamples"
        >> beam.io.WriteToTFRecord(
            os.path.join(output_path, _EXAMPLES_FILE_NAME),
            file_name_suffix=".gz",
            coder=beam.coders.ProtoCoder(tf.train.Example),
        )
    )
