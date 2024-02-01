variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
}

variable "region" {
  type        = string
  description = "Google Cloud Resource Region"
}

variable "zone" {
  type        = string
  description = "Google Cloud Region Zone"
}

variable "gcp_service_list" {
  description = "The list of apis necessary for the project"
  type        = list(string)
}
