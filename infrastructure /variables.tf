variable "gcp_project_id" {
  description = "Identyfikator Twojego projektu w Google Cloud."
  type        = string
}

variable "gcp_region" {
  description = "Region, w którym będą tworzone zasoby."
  type        = string
  default     = "us-central1"
}

variable "vertex_ai_bucket_name" {
  description = "Nazwa bucketa GCS dla artefaktów potoków Vertex AI."
  type        = string
}

variable "artifacts_bucket_name" {
  description = "Nazwa bucketa GCS na artefakty modeli."
  type        = string
}

variable "data_bucket_name" {
  description = "Nazwa bucketa GCS na dane (np. pliki CSV)."
  type        = string
}

variable "service_account_email" {
  description = "Email of the service account"
  type        = string
  default     = "vertex-ai-runner@mlops-on-gcp-s25537.iam.gserviceaccount.com"
}

variable "github_repo_name" {
  description = "Nazwa repozytorium GitHub."
  type        = string
}

variable "github_connection_id" {
  description = "Pełny identyfikator istniejącego połączenia Cloud Build z GitHub. Przykład: projects/nazwa-projektu/locations/region/connections/nazwa-polaczenia"
  type        = string
}

variable "github_user_or_org" {
  description = "Twój login użytkownika lub nazwa organizacji na GitHub."
  type        = string
}

variable "deployment_endpoint_name" {
  description = "Nazwa punktu końcowego (Endpoint) w Vertex AI, na którym wdrażany jest model."
  type        = string
  default     = "puffin-endpoint"
}