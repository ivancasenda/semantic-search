"""Tests for for pipeline.components.MatchingEngineIndexer.executor"""
import os

import tensorflow as tf
from tfx.types import standard_artifacts
from tfx.utils import io_utils
from tfx.dsl.io import fileio

from pipeline.components.matching_engine_indexer import executor, component_spec

_TEST_SOURCE_FOLDER = "testdata"
_TEST_OUTPUT_FOLDER = "testoutput"
_TEST_COMPONENT_ID = "test_component"
_TEST_INFERENCE_RESULT_FOLDER = "inference_result"
_TEST_FEATURE_VECTOR_FOLDER = "feature_vector"


class ExecutorTest(tf.test.TestCase):
    def setUp(self):
        super().setUp()
        self._source_data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), _TEST_SOURCE_FOLDER
        )
        self._output_data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), _TEST_OUTPUT_FOLDER
        )
        self.component_id = _TEST_COMPONENT_ID

        # Create input dict.
        self._inference_result = standard_artifacts.InferenceResult()
        inference_result_path = os.path.join(
            self._source_data_dir, _TEST_INFERENCE_RESULT_FOLDER
        )
        self._inference_result.uri = os.path.join(
            self._output_data_dir, _TEST_INFERENCE_RESULT_FOLDER
        )
        io_utils.copy_dir(inference_result_path, self._inference_result.uri)

        self._input_dict = {
            component_spec.INFERENCE_RESULT_KEY: [self._inference_result]
        }

        # Create output dict.
        self._feature_vector = component_spec.FeatureVector()
        self._feature_vector.uri = os.path.join(
            self._output_data_dir, _TEST_FEATURE_VECTOR_FOLDER
        )

        self._output_dict_ir = {
            component_spec.FEATURE_VECTOR_KEY: [self._feature_vector]
        }

        # Create exe properties.
        self._exec_properties = {
            "component_id": self.component_id,
        }

        # Create context
        self._tmp_dir = os.path.join(self._output_data_dir, ".temp")
        self._context = executor.Executor.Context(tmp_dir=self._tmp_dir, unique_id="2")

    def testRun(self):
        indexer = executor.Executor(self._context)
        indexer.Do(self._input_dict, self._output_dict_ir, self._exec_properties)

        # Check outputs.
        self.assertTrue(
            fileio.exists(
                os.path.join(self._feature_vector.uri, "embeddings-00000-of-00001.json")
            )
        )


if __name__ == "__main__":
    tf.test.main()
