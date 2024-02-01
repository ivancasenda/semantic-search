import os

from tfx import v1 as tfx
from absl import logging

from tfx.orchestration.data_types import RuntimeParameter
from tfx.orchestration.kubeflow.v2 import kubeflow_v2_dag_runner

from pipeline import config, pipeline


def run() -> str:
    """
    Runs the TFX pipeline using Kubeflow V2 as the orchestrator.

    Returns:
        str: The path to the generated pipeline definition file.
    """
    pipeline_definition_file = config.PIPELINE_NAME + ".json" # Define the pipeline definition file name

    # Configure the Kubeflow V2 Dag Runner
    runner_config = kubeflow_v2_dag_runner.KubeflowV2DagRunnerConfig(
        default_image=config.PIPELINE_IMAGE
    )

    # Run the TFX pipeline
    kubeflow_v2_dag_runner.KubeflowV2DagRunner(
        output_dir=config.GCS_BUCKET,
        config=runner_config,
        output_filename=pipeline_definition_file,
    ).run(
        pipeline.create_pipeline(
            pipeline_name=config.PIPELINE_NAME,
            pipeline_root=config.PIPELINE_ROOT,
            bigquery_input_config=RuntimeParameter(
                name="bigquery_input_config", ptype=str
            ),
            model_uri=config.INFERRER_MODEL_GCS_DIR,
            update_index=RuntimeParameter(name="update_index", ptype=str, default=""),
            schema_path=config.SCHEMA_PATH,
            example_gen_beam_args=config.EXAMPLE_GEN_BEAM_ARGS,
            bulk_inferrer_beam_args=config.BULK_INFERRER_BEAM_ARGS,
            matching_engine_indexer_beam_args=config.MATCHING_ENGINE_INDEXER_BEAM_ARGS,
            ai_platform_serving_args=config.GCP_AI_PLATFORM_PREDICTION_ARGS,
            metadata_connection_config=tfx.orchestration.metadata.sqlite_metadata_connection_config(
                config.METADATA_PATH
            ),
        )
    )
    # Return the path to the generated pipeline definition file
    return os.path.join(config.GCS_BUCKET, pipeline_definition_file)


if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    run()
