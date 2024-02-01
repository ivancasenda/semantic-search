# Semantic Search Pipeline

This GitHub repository houses the source code and documentation for machine learning pipeline built using TFX. The project aims to create a scalable and automated pipeline that takes data from Google BigQuery, performs batch inference using a TensorFlow saved model, and updates Vertex AI Matching Engine Index. The entire process is orchestrated using Google Cloud Vertex Pipelines and scheduled for periodic execution with Cloud Scheduler.

![ML Pipeline](https://search.ivancasenda.com/assets/pipeline.png)

## Table of Contents

- [System Overview](#system-overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)

## System Overview

- #### BigQueryExampleGen

  As part of our project, we are utilizing a publicly available Stack Overflow dataset that is stored in BigQuery. To incorporate this data into our pipeline, we are using the BigQueryExampleGen component. This component is responsible for retrieving data from BigQuery and forwarding it to the pipeline. Additionally, it delegates its job to Dataflow to enable us to execute Apache Beam pipelines effectively in a fully distributed manner.

- #### ImportModel

  The ImportModel component's role is to retrieve a TensorFlow saved model from Google Cloud Storage and make it available for use by other components within the pipeline.

- #### VertexAIBulkInferrer

  The VertexAIBulkInferrer is a custom TFX component that performs batch inference. It utilizes Vertex AI Predictions to host the model and Dataflow to perform remote predictions on the hosted model.

- #### MatchingEngineIndexer

  Finally, the MatchingEngineIndexer custom TFX component structures and formats the embeddings from the inference result to meet the requirements of Vertex AI Matching Engine and updates the Matching Engine Index.

- #### Cloud Scheduler
  To ensure that our search results are always up to date with the latest data, we want to periodically run the pipeline with Cloud Scheduler. When the scheduled Cloud Scheduler publishes a topic to Cloud Pub/Sub, a Cloud Function subscribed to the topic will trigger a pipeline run. This will allow us to keep our search results current with minimal manual intervention.

## Prerequisites

Before getting started, make sure you have the following prerequisites:

- Google Cloud Platform (GCP) resources created from [semantic-search-terraform](https://github.com)
- Google Cloud SDK (`gcloud`) installed and authenticated.

## Getting Started

To get started with this project, please follow these steps:

1. Set up the necessary configurations for Google Cloud in `pipeline/config.py` with GCP resources created using terraform.

2. Follow the steps in `notebook.ipynb` for running and deploying pipeline.
