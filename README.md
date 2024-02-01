# Semantic Search in Action

Semantic search delivers more relevant results by using the intent and contextual meaning behind a search query. This demo performs a semantic search on Stackoverflow datasets. It uses MiniLM Sentence Transformers Model to generate the embedding and Vertex AI Vector Search to index and query the embeddings. The index is periodically updated using TFX pipeline.

[search.ivancasenda.com](https://search.ivancasenda.com)

<p align="center">
  <img src="demo.gif" alt="demo" width="1000" style="border-radius:1%"/>
</p>

## Project Structure

This repository comprise of Angular frontend, Python FastAPI backend, Terraform project, and a Machine Learning pipeline.

- [`semantic-search-fe/`](semantic-search-fe): This directory contains the Angular frontend application. It's responsible for the user interface and interactions.

- [`semantic-search-be/`](semantic-search-be): Here lies the Python FastAPI backend. It serves as the server-side logic, handling search requests from the frontend.

- [`semantic-search-terraform/`](semantic-search-terraform): The Terraform project defines and provisions the necessary google cloud (GCP) resources for deploying and running the application.

- [`semantic-search-pipeline/`](semantic-search-pipeline): The Machine Learning pipeline resides in this directory. It handles data ingestion, batch inference, and updating the embedings index.

## Getting Started

- Please refer to the README within that directory for instructions on setting up and getting started.

## Dependencies

- **Angular Frontend:**

  - Node.js
  - Angular CLI
  - NgRx
  - Tailwind CSS
  - Firebase Hosting

- **Python FastAPI Backend:**

  - Python 3.x
  - FastAPI
  - Google Cloud SDK

- **Terraform Project:**

  - Terraform CLI
  - Cloud Provider GCP CLI

- **ML Pipeline:**
  - Python 3.x
  - Tensorflow Extended (TFX)
