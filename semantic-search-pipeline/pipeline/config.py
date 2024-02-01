import os
from pipeline.components.vertex_ai_bulk_inferrer import constants as const

# Define constants and configuration parameters for the semantic search pipeline

# Pipeline metadata
PIPELINE_NAME = "semantic-search-pipeline"
GOOGLE_CLOUD_PROJECT = "stackoverflow-semantic-search"
GOOGLE_CLOUD_REGION = "asia-southeast1"

# GCP Resources from Terraform Output
GCS_BUCKET = "gs://stackoverflow-semantic-search-storage"
ARTIFACT_REGISTRY_REPO = "stackoverflow-semantic-search-docker"
SERVICE_ACCOUNT = "svc-acc@stackoverflow-semantic-search.iam.gserviceaccount.com"

# Tensorflow Saved Model Directory
INFERRER_MODEL_GCS_DIR = (
    f"{GCS_BUCKET}/models/multi-qa-MiniLM-L6-dot-v1-inferrer/1/model.savedmodel"
)

# Google Artifact Registry Repository for pipeline docker image
PIPELINE_IMAGE = f"{GOOGLE_CLOUD_REGION}-docker.pkg.dev/{GOOGLE_CLOUD_PROJECT}/{ARTIFACT_REGISTRY_REPO}/{PIPELINE_NAME}"
SCHEMA_PATH = f"{GCS_BUCKET}/semantic-search-schema.pbtxt"

# TFX pipeline produces many output files and metadata. All output data will be
# stored under this OUTPUT_DIR.
PIPELINE_ROOT = os.path.join(GCS_BUCKET, "tfx", "tfx_pipeline_output", PIPELINE_NAME)
METADATA_PATH = os.path.join(
    GCS_BUCKET, "tfx", "tfx_metadata", PIPELINE_NAME, "metadata.db"
)

# VPC Network created in terraform
VPC_NETWORK = (
    "projects/500376812545/global/networks/stackoverflow-semantic-search-vpc-network"
)

# Vertex AI Model Endpoint configuration
PREDICTION_IMAGE = (
    "us-docker.pkg.dev/vertex-ai-restricted/prediction/tf_opt-gpu.2-11:latest"
)
PREDICTION_REGION = "us-central1"
GCP_AI_PLATFORM_PREDICTION_ARGS = {
    const.ENABLE_VERTEX_KEY: True,
    const.VERTEX_REGION_KEY: PREDICTION_REGION,
    const.VERTEX_CONTAINER_IMAGE_URI_KEY: PREDICTION_IMAGE,
    const.SERVING_ARGS_KEY: {
        "project_id": GOOGLE_CLOUD_PROJECT,
        "endpoint_name": PIPELINE_NAME.replace("-", "_") + "_endpoint",
        "machine_type": "n1-standard-4",
        "min_replica_count": 1,
        "max_replica_count": 1,
        "accelerator_type": "NVIDIA_TESLA_T4",  # NVIDIA_TESLA_V100
        "accelerator_count": 1,
        "service_account": SERVICE_ACCOUNT,
        "network": VPC_NETWORK,
    },
    const.BATCH_PARAMETERS_ARGS_KEY: {  # proto/model_spec.proto BatchParameters
        "min_batch_size": 32,
        "max_batch_size": 32,
        "target_batch_overhead": 0.05,
        "target_batch_duration_secs": 10,
        "variance": 0.25,
    },
}

# Beam configuration for direct runner (non dataflow)
BIG_QUERY_WITH_DIRECT_RUNNER_BEAM_PIPELINE_ARGS = [
    "--project=" + GOOGLE_CLOUD_PROJECT,
    "--temp_location=" + os.path.join(GCS_BUCKET, "tmp"),
]

# Dataflow jobs configuration https://cloud.google.com/dataflow/docs/reference/pipeline-options
DATAFLOW_MACHINE_TYPE = "n1-standard-4"
DATAFLOW_MAX_WORKERS = 1
DATAFLOW_DISK_SIZE_GB = 100
DATAFLOW_STAGING_LOCATION = os.path.join(GCS_BUCKET, "dataflow", "dataflow-staging")
DATAFLOW_TEMP_LOCATION = os.path.join(GCS_BUCKET, "dataflow", "dataflow-temp")
DATAFLOW_REGION = "us-central1"
DATAFLOW_ZONE = f"{DATAFLOW_REGION}-a"

EXAMPLE_GEN_BEAM_ARGS = [
    "--runner=DataflowRunner",
    "--project=" + GOOGLE_CLOUD_PROJECT,
    "--region=" + DATAFLOW_REGION,
    "--worker_zone=" + DATAFLOW_ZONE,
    "--service_account_email=" + SERVICE_ACCOUNT,
    "--machine_type=" + DATAFLOW_MACHINE_TYPE,
    "--experiments=use_runner_v2",
    "--max_num_workers=" + str(DATAFLOW_MAX_WORKERS),
    "--disk_size_gb=" + str(DATAFLOW_DISK_SIZE_GB),
    "--staging_location=" + str(DATAFLOW_STAGING_LOCATION),
    "--temp_location=" + str(DATAFLOW_TEMP_LOCATION),
    "--sdk_container_image=" + str(PIPELINE_IMAGE),
    "--sdk_location=container",
]

BULK_INFERRER_BEAM_ARGS = [
    "--runner=DataflowRunner",
    "--project=" + GOOGLE_CLOUD_PROJECT,
    "--region=" + DATAFLOW_REGION,
    "--worker_zone=" + DATAFLOW_ZONE,
    "--service_account_email=" + SERVICE_ACCOUNT,
    "--machine_type=" + DATAFLOW_MACHINE_TYPE,
    "--experiments=use_runner_v2",
    "--max_num_workers=" + str(DATAFLOW_MAX_WORKERS),
    "--disk_size_gb=" + str(DATAFLOW_DISK_SIZE_GB),
    "--staging_location=" + str(DATAFLOW_STAGING_LOCATION),
    "--temp_location=" + str(DATAFLOW_TEMP_LOCATION),
    "--sdk_container_image=" + str(PIPELINE_IMAGE),
    "--sdk_location=container",
    "--network=" + VPC_NETWORK.split("/")[-1],
]

MATCHING_ENGINE_INDEXER_BEAM_ARGS = [
    "--runner=DataflowRunner",
    "--project=" + GOOGLE_CLOUD_PROJECT,
    "--region=" + DATAFLOW_REGION,
    "--worker_zone=" + DATAFLOW_ZONE,
    "--service_account_email=" + SERVICE_ACCOUNT,
    "--machine_type=" + DATAFLOW_MACHINE_TYPE,
    "--experiments=use_runner_v2",
    "--max_num_workers=" + str(DATAFLOW_MAX_WORKERS),
    "--disk_size_gb=" + str(DATAFLOW_DISK_SIZE_GB),
    "--staging_location=" + str(DATAFLOW_STAGING_LOCATION),
    "--temp_location=" + str(DATAFLOW_TEMP_LOCATION),
    "--sdk_container_image=" + str(PIPELINE_IMAGE),
    "--sdk_location=container",
]
