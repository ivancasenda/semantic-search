"""Tests for pipeline.components.MatchingEngineIndexer.component."""

import tensorflow as tf

from pipeline.components.matching_engine_indexer import component, component_spec
from tfx.types import channel_utils
from tfx.types import standard_artifacts


class ComponentTest(tf.test.TestCase):
    def setUp(self):
        super().setUp()
        self._inference_result = channel_utils.as_channel(
            [standard_artifacts.InferenceResult()]
        )

    def testConstruct(self):
        indexer = component.MatchingEngineIndexerComponent(
            inference_result=self._inference_result
        )
        self.assertEqual(
            component_spec.FeatureVector.TYPE_NAME,
            indexer.outputs[component_spec.FEATURE_VECTOR_KEY].type_name,
        )


if __name__ == "__main__":
    tf.test.main()
