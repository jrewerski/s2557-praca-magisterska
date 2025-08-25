terraform {
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 6.0"
        }
      }
    }
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
    }

locals {
  all_bucket_names = toset([
    var.vertex_ai_bucket_name,
    var.artifacts_bucket_name,
    var.data_bucket_name,
  ])
}

resource "google_storage_bucket" "mlops_buckets" {
  for_each = local.all_bucket_names

  name     = each.value
  location = var.gcp_region
  force_destroy               = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "penguins_csv" {
  name   = "penguins.csv"
  # Pełna ścieżka do pliku lokalnego
  source = "../data/penguins.csv" 
  # Nazwa bucketa docelowego
  bucket = "s25537-mlops-data-bucket"
  depends_on = [google_storage_bucket.mlops_buckets]
}

resource "google_service_account" "vertex_ai_runner" {
  account_id   = "vertex-ai-runner"
  display_name = "Service Account for Vertex AI Pipelines"
}

# Uprawnienia dla konta serwisowego
resource "google_project_iam_member" "vertex_ai_runner_permissions" {
  for_each = toset([
    "roles/aiplatform.user",       
    "roles/storage.objectAdmin",     
    "roles/pubsub.publisher",        
    "roles/artifactregistry.writer", 
    "roles/iam.serviceAccountUser", 
    "roles/logging.logWriter"
  ])
  project = var.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.vertex_ai_runner.email}"
}

resource "google_artifact_registry_repository" "mlops_repo" {
  provider      = google-beta
  project       = var.gcp_project_id
  location      = var.gcp_region
  repository_id = "mlops-repo"
  description   = "Docker repository for MLOps pipelines"
  format        = "DOCKER"
  depends_on    = [google_project_service.gcp_apis]
}

# Blok do zarządzania włączaniem API w projekcie GCP
resource "google_project_service" "gcp_apis" {
  for_each = toset([
    "aiplatform.googleapis.com",         
    "cloudbuild.googleapis.com",         
    "artifactregistry.googleapis.com",   
    "cloudresourcemanager.googleapis.com", 
    "iam.googleapis.com",                
    "pubsub.googleapis.com",             
    "storage.googleapis.com"             
  ])

  project                    = var.gcp_project_id
  service                    = each.value
}


resource "google_cloudbuildv2_repository" "github_repo" {
  provider          = google-beta
  project           = var.gcp_project_id
  # Upewnij się, że region jest zgodny z regionem Twojego połączenia (np. us-central1)
  location          = "us-central1" 
  name              = var.github_repo_name
  parent_connection = var.github_connection_id
  remote_uri        = "https://github.com/${var.github_user_or_org}/${var.github_repo_name}.git" 
}

resource "google_pubsub_topic" "deployment-topic" {
  name = "model-deployment-topic"
}


# Stworzenie wyzwalacza (triggera) na podstawie powiązanego repozytorium
resource "google_cloudbuild_trigger" "main-pipeline-trigger" {
  project     = var.gcp_project_id
  location    = var.gcp_region
  name        = "deployment-trigger-terraform"
  description = "Uruchamia główny potok CI/CD po push do gałęzi main"

  repository_event_config {
    repository = google_cloudbuildv2_repository.github_repo.id
    push {
      branch = "^main$"
    }
  }

  filename = "cloudbuild/cloudbuild.yaml"

  substitutions = {
    _REGION                   = var.gcp_region
    _SERVICE_ACCOUNT          = google_service_account.vertex_ai_runner.email
    _PIPELINE_GCS_PATH        = "gs://${var.vertex_ai_bucket_name}"
    _CUSTOM_COMPONENT_IMAGE_REPO = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.mlops_repo.repository_id}/training-components"
    _COMPONENTS_DIR_PATH      = "03-vertex-ai-pipelines/training-pipeline/components"
    _PIPELINE_NAME            = "training-pipeline"
    _PIPELINE_SCRIPT_PATH     = "03-vertex-ai-pipelines/training-pipeline/runner.py"
    _PARAMETER_FILE           = "config/training-params.json"
    _GCS_DATA_PATH               = "gs://${var.data_bucket_name}/penguins.csv"
  }

  service_account = google_service_account.vertex_ai_runner.id
  depends_on      = [google_cloudbuildv2_repository.github_repo]
}

resource "google_cloudbuild_trigger" "deployment_pipeline_trigger" {
  project     = var.gcp_project_id
  location    = var.gcp_region
  name        = "trigger-deployment-from-pubsub"
  description = "Uruchamia potok wdrożeniowy po otrzymaniu wiadomości o nowym modelu"

  # Konfiguracja źródła jako wiadomości Pub/Sub
  pubsub_config {
    topic = google_pubsub_topic.deployment-topic.id
  }

  # Wskazanie, że plik builda znajduje się w repozytorium GitHub
  git_file_source {
    path      = "cloudbuild/run-deployment-pipeline.yaml"
    repo_type = "GITHUB"
    uri       = "https://github.com/${var.github_user_or_org}/${var.github_repo_name}.git"
    revision  = "refs/heads/main"
  }

  # Wymaga ręcznego zatwierdzenia w konsoli Cloud Build
  approval_config {
    approval_required = true
  }

  # Zmienne przekazywane do procesu budowania
  substitutions = {
    _REGION              = var.gcp_region
    _SERVICE_ACCOUNT     = google_service_account.vertex_ai_runner.email
    _PIPELINE_GCS_PATH   = "gs://${var.vertex_ai_bucket_name}"
    _ENDPOINT_NAME       = var.deployment_endpoint_name
    _MODEL_RESOURCE_NAME = "$(body.message.attributes.model_resource_name)"
  }

  # Użyj konta serwisowego, które stworzyliśmy
  service_account = google_service_account.vertex_ai_runner.id
}