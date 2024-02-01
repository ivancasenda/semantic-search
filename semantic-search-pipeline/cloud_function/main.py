"""Cloud Function to be triggered by Pub/Sub."""

import os
import json
import logging
from datetime import datetime, timedelta

from google.cloud import aiplatform
from google.cloud import storage


QUERY = "SELECT id, CONCAT(title, '\\n', LEFT(body, 100)) as title_body, tags FROM bigquery-public-data.stackoverflow.posts_questions WHERE creation_date BETWEEN '{}' AND '{}' AND score > 0 ORDER BY creation_date"
MATCHING_ENGINE_INDEX = ""


def is_file_exist(gcs_path):
    """
    Checks if a file exists in Google Cloud Storage.

    Args:
        gcs_path (str): The path to the file in Google Cloud Storage.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    storage_client = storage.Client()

    path_parts = gcs_path.replace("gs://", "").split("/")
    bucket_name = path_parts[0]
    blob_name = "/".join(path_parts[1:])

    bucket = storage_client.bucket(bucket_name)
    blob = storage.Blob(bucket=bucket, name=blob_name)

    if not blob.exists(storage_client):
        return False
    return True


def trigger_pipeline(event, context):
    """
    Cloud Function to be triggered by Pub/Sub.

    Args:
        event (dict): The dictionary with data specific to this type of event.
        context (google.cloud.functions.Context): The Cloud Functions event context.

    Returns:
        str: A string indicating the completion status of the function.
    """
    # Parse the environment variables.
    project = os.getenv("PROJECT")
    region = os.getenv("REGION")
    gcs_pipeline_file_location = os.getenv("GCS_PIPELINE_FILE_LOCATION")
    pipeline_name = os.getenv("PIPELINE_NAME")
    service_account = os.getenv("SERVICE_ACCOUNT")

    if not project:
        raise ValueError("Environment variable GCP_PROJECT is not set.")
    if not region:
        raise ValueError("Environment variable GCP_REGION is not set.")
    if not gcs_pipeline_file_location:
        raise ValueError("Environment variable GCS_PIPELINE_FILE_LOCATION is not set.")
    if not is_file_exist(gcs_pipeline_file_location):
        raise ValueError(f"{gcs_pipeline_file_location} does not exist.")

    if not pipeline_name:
        pipeline_name = "pipeline_run"

    # Initialize Vertex AI API client and submit for pipeline execution.
    aiplatform.init(project=project, location=region)

    date_start = datetime.now().date() + timedelta(days=-406)
    date_end = date_start + timedelta(days=1)

    bigquery_input_config = {
        "splits": [
            {
                "name": "single_split",
                "pattern": QUERY.format(str(date_start), str(date_end)),
            }
        ]
    }

    pipeline_parameter = {
        "bigquery_input_config": json.dumps(bigquery_input_config),
        "update_index": MATCHING_ENGINE_INDEX,
    }

    print("Pipeline Run Parameter: ", pipeline_parameter)

    pipeline = aiplatform.PipelineJob(
        display_name=pipeline_name,
        template_path=gcs_pipeline_file_location,
        parameter_values=pipeline_parameter,
    )

    logging.info("Submitting Pipeline Job")
    if service_account:
        # Run pipeline with service account
        pipeline.submit(service_account=service_account)
    else:
        pipeline.submit()

    return "Done"
