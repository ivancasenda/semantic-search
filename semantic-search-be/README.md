# FastAPI Backend Service for Semantic Search

This repository contains FastAPI code for a backend service that serves search requests. The service is designed to be deployed on Google Cloud Run, a fully managed compute platform that automatically scales your stateless containers.

![Diagram](https://search.ivancasenda.com/assets/architecture.png)

## Table of Contents

- [System Overview](#system-overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)

## System Overview

- #### Search Query

  After the user enters a search query, the application sends a request to the FastAPI service backend hosted on Cloud Run.

- #### VPC Connector

  The Cloud Run Service is securely connected to the Virtual Private Cloud (VPC) network using a VPC Connector. This ensures that communication is private and secure.

- #### Embedding Generation

  The service processes the user's search query by transforming it into an embedding using the Sentence Transformers model, which is hosted on Vertex AI Predictions. This step involves converting the search query into a numerical representation that can be used for similarity matching.

- #### Nearest Neighbor Search

  The generated embedding is then passed to the Vertex AI Matching Engine, which identifies the nearest neighbors based on the embedding similarity (dot product). This step determines which items or posts are most similar to the user's query.

- #### Neighbor ID Retrieval
  The Matching Engine returns the IDs of the nearest neighbors, which are used to retrieve relevant posts. To efficiently retrieve the posts associated with the neighbor IDs, the system queries a Redis instance hosted on Cloud Memorystore. Redis offers lightning-fast access to relevant data while ensuring high performance and scalability.

## Prerequisites

Before getting started, make sure you have the following prerequisites:

- Google Cloud Platform (GCP) resources created from [semantic-search-terraform](https://github.com)
- Deployed Vertex AI Predictions and Vertex AI Matching Engine from [semantic-search-pipeline](https://github.com)

## Getting Started

Follow the steps in `notebook.ipynb` to get started with this FastAPI backend service.
