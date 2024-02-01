# Semantic Search Terraform

This repository contains Terraform code for creating various Google Cloud Platform (GCP) resources for the semantic search in action [project](https://www.github.com). The code provisions GCP services, storage, network, firewalls, and IAM roles.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Resources Created](#resources-created)

## Prerequisites

Before using this Terraform code, make sure you have the following prerequisites in place:

- [Terraform](https://www.terraform.io/downloads.html) installed on your local machine.
- Google Cloud Platform account and project.
- Google Cloud SDK (`gcloud`) installed and authenticated.

## Usage

1. Clone this repository to your local machine.
2. Navigate to the repository directory.
3. Define the required variables, such as `project_id`, `region`, `zone`, and `gcp_service_list` in `terraform.tfvars`.
4. Initialize the Terraform configuration by running:
   ```bash
   terraform init
   ```
5. Plan the infrastructure to see the changes that Terraform will apply:
   ```bash
   terraform plan
   ```
6. If the plan looks good, apply the changes by running:
   ```bash
   terraform apply
   ```
7. Confirm the changes by typing "yes" when prompted.

## Resources Created

The Terraform code in this repository creates the following GCP resources:

- Enable Google Cloud Platform services specified in `var.gcp_service_list`.
- Create a Google Cloud Storage bucket.
- Create an Artifact Registry repository for Docker images.
- Create a VPC network with auto-created subnetworks.
- Define firewall rules to allow ICMP, internal traffic, RDP, and SSH access.
- Allocate an internal IP address range.
- Establish a private service connection.
- Create a VPC access connector for Cloud Run.
- Create a service account and assign various IAM roles to it.
