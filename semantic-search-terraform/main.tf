# Enable Google Cloud Platform Service / API
resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  service  = each.key
}


# Create Google Cloud Storage Bucket
resource "google_storage_bucket" "storage" {
  name          = "${var.project_id}-storage"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  force_destroy = true

  depends_on = [google_project_service.gcp_services]
}


# Create Artifact Registry Repository for Docker Image
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "${var.project_id}-docker"
  description   = "Docker Repository"
  format        = "DOCKER"

  depends_on = [google_project_service.gcp_services]
}


# Create VPC Network
resource "google_compute_network" "vpc-network" {
  name                    = "${var.project_id}-vpc-network"
  auto_create_subnetworks = true

  depends_on = [google_project_service.gcp_services]
}


# VPC Firewall Allow ICMP
resource "google_compute_firewall" "vpc-network-allow-icmp" {
  name    = "${var.project_id}-vpc-network-allow-icmp"
  network = google_compute_network.vpc-network.name

  allow {
    protocol = "icmp"
  }

  source_ranges = ["0.0.0.0/0"]

  priority = 65534

  depends_on = [google_project_service.gcp_services, google_compute_network.vpc-network]
}


# VPC Firewall Allow Internal IP Address
resource "google_compute_firewall" "vpc-network-allow-internal" {
  name    = "${var.project_id}-vpc-network-allow-internal"
  network = google_compute_network.vpc-network.name

  allow {
    protocol = "all"
  }

  source_ranges = ["10.128.0.0/9"]

  priority = 65534

  depends_on = [google_project_service.gcp_services, google_compute_network.vpc-network]
}


# VPC Firewall Allow RDP
resource "google_compute_firewall" "vpc-network-allow-rdp" {
  name    = "${var.project_id}-vpc-network-allow-rdp"
  network = google_compute_network.vpc-network.name

  allow {
    protocol = "tcp"
    ports    = ["3389"]
  }

  source_ranges = ["0.0.0.0/0"]

  priority = 65534

  depends_on = [google_project_service.gcp_services, google_compute_network.vpc-network]
}


# VPC Firewall Allow SSH
resource "google_compute_firewall" "vpc-network-allow-ssh" {
  name    = "${var.project_id}-vpc-network-allow-ssh"
  network = google_compute_network.vpc-network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]

  priority = 65534

  depends_on = [google_project_service.gcp_services, google_compute_network.vpc-network]
}


# Create IP Address Allocation Range
resource "google_compute_global_address" "private-ip-alloc" {
  name          = "${var.project_id}-private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc-network.id

  depends_on = [google_project_service.gcp_services, google_compute_network.vpc-network]
}


# VPC Peer Google Service Network (Private Service Connection)
resource "google_service_networking_connection" "private-service-connection" {
  network                 = google_compute_network.vpc-network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private-ip-alloc.name]

  depends_on = [google_project_service.gcp_services, google_compute_network.vpc-network, google_compute_global_address.private-ip-alloc]
}


# Create VPC Access Connector for Cloud Run to access VPC
resource "google_vpc_access_connector" "conn" {
  name          = "vpc-conn"
  network       = google_compute_network.vpc-network.id
  ip_cidr_range = "10.2.0.0/28"
  min_instances = 2
  max_instances = 3
  machine_type  = "f1-micro"
  region        = var.region

  depends_on = [google_project_service.gcp_services]
}


# Create Service Account
resource "google_service_account" "project_sa" {
  account_id   = "svc-acc"
  display_name = "Project Service Account"
}

# Assign Roles to Service Account
resource "google_project_iam_member" "artifactregistry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "redis_editor" {
  project = var.project_id
  role    = "roles/redis.editor"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "dataflow_admin" {
  project = var.project_id
  role    = "roles/dataflow.admin"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "storage_objectAdmin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "iam_serviceAccountUser" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "cloudfunctions_admin" {
  project = var.project_id
  role    = "roles/cloudfunctions.admin"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}

resource "google_project_iam_member" "cloudscheduler_admin" {
  project = var.project_id
  role    = "roles/cloudscheduler.admin"
  member  = "serviceAccount:${google_service_account.project_sa.email}"

  depends_on = [google_service_account.project_sa]
}




