from tfx import v1 as tfx

from typing import Any, List, Optional
from ml_metadata.proto import metadata_store_pb2

from tfx.v1.dsl import Importer
from tfx.types import standard_artifacts

from tfx.orchestration.data_types import RuntimeParameter
from tfx.proto import example_gen_pb2

from pipeline.components.vertex_ai_bulk_inferrer.component import (
    VertexAIBulkInferrerComponent,
)
from pipeline.components.matching_engine_indexer.component import (
    MatchingEngineIndexerComponent,
)

from typing import Dict, Text


def create_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    bigquery_input_config: RuntimeParameter,
    model_uri: str,
    update_index: Optional[RuntimeParameter] = None,
    metadata_connection_config: Optional[metadata_store_pb2.ConnectionConfig] = None,
    example_gen_beam_args: Optional[List] = None,
    bulk_inferrer_beam_args: Optional[List] = None,
    matching_engine_indexer_beam_args: Optional[List] = None,
    ai_platform_serving_args: Optional[Dict[Text, Any]] = None,
) -> tfx.dsl.Pipeline:
    """
    Creates and returns a TFX pipeline.

    Args:
        pipeline_name (str): The name of the TFX pipeline.
        pipeline_root (str): The root directory for storing pipeline artifacts.
        bigquery_input_config (RuntimeParameter): Runtime parameter for BigQuery input configuration.
        model_uri (str): URI to the pre-trained model for import.
        update_index (Optional[RuntimeParameter]): Runtime parameter for updating the index.
        metadata_connection_config (Optional[metadata_store_pb2.ConnectionConfig]): Metadata connection configuration.
        example_gen_beam_args (Optional[List]): Additional Beam arguments for the ExampleGen component.
        bulk_inferrer_beam_args (Optional[List]): Additional Beam arguments for the Bulk Inferrer component.
        matching_engine_indexer_beam_args (Optional[List]): Additional Beam arguments for the Matching Engine Indexer component.
        ai_platform_serving_args (Optional[Dict[Text, Any]]): Additional arguments for AI Platform Serving.

    Returns:
        tfx.dsl.Pipeline: The configured TFX pipeline.
    """
    components = []

    # ExampleGen component for ingesting data from BigQuery
    example_gen = tfx.extensions.google_cloud_big_query.BigQueryExampleGen(
        input_config=bigquery_input_config, output_config=example_gen_pb2.Output()
    )
    if example_gen_beam_args is not None:
        example_gen.with_beam_pipeline_args(example_gen_beam_args)
    components.append(example_gen)

    # Importer component for importing a pre-trained model
    model_importer = Importer(
        source_uri=model_uri, artifact_type=standard_artifacts.Model, reimport=False
    ).with_id("ImportModel")
    components.append(model_importer)

    # Bulk Inferrer component for performing bulk inference using Vertex AI
    bulk_inferrer = VertexAIBulkInferrerComponent(
        examples=example_gen.outputs["examples"],
        model=model_importer.outputs["result"],
        custom_config=ai_platform_serving_args,
    )
    if bulk_inferrer_beam_args is not None:
        bulk_inferrer.with_beam_pipeline_args(bulk_inferrer_beam_args)
    components.append(bulk_inferrer)

    # Matching Engine Indexer component for indexing inference results
    indexer = MatchingEngineIndexerComponent(
        inference_result=bulk_inferrer.outputs["inference_result"],
        update_index=update_index,
    )
    if matching_engine_indexer_beam_args is not None:
        indexer.with_beam_pipeline_args(matching_engine_indexer_beam_args)
    components.append(indexer)

    # Create and return the TFX pipeline
    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        metadata_connection_config=metadata_connection_config,
        enable_cache=True,
    )
