import sys
import argparse
import json
from google.cloud import aiplatform

def main(args):


    aiplatform.init(project=args.project_id, location=args.region)

    # Wczytaj parametry z pliku JSON 
    with open(args.parameter_file, 'r') as f:
        pipeline_parameters = json.load(f).get("parameter_values", {})

    pipeline_parameters['project_id'] = args.project_id
    pipeline_parameters['region'] = args.region

    if args.gcs_data_path:
        pipeline_parameters['gcs_data_path'] = args.gcs_data_path
    if args.endpoint_name:
        pipeline_parameters['endpoint_name'] = args.endpoint_name
    if args.model_resource_name:
        pipeline_parameters['model_resource_name'] = args.model_resource_name

    print(f"Submitting pipeline job with parameters: {pipeline_parameters}")

    # Utwórz zadanie potoku
    job = aiplatform.PipelineJob(
        display_name=args.display_name,
        template_path=args.pipeline_spec_uri,
        pipeline_root=args.pipeline_root,
        parameter_values=pipeline_parameters,
        enable_caching=False,
    )

    # Prześlij zadanie, używając podanego konta serwisowego
    job.submit(service_account=args.service_account)  
    print(f"Pipeline job '{job.display_name}' submitted. View it at: {job.resource_name}")
    print("Waiting for pipeline to complete...")
    job.wait()
    print("Pipeline finished.")
    if job.state == aiplatform.gapic.PipelineState.PIPELINE_STATE_SUCCEEDED:
        print("Pipeline run succeeded.")
    else:
        print(f"Pipeline run failed. Final state: {job.state}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger a Vertex AI Pipeline")
    parser.add_argument("--project-id", type=str, required=True, help="Google Cloud Project ID")
    parser.add_argument("--region", type=str, required=True, help="Google Cloud Region")
    parser.add_argument("--pipeline-spec-uri", type=str, required=True, help="GCS URI of the compiled pipeline JSON")
    parser.add_argument("--display-name", type=str, required=True, help="Display name for the pipeline run")
    parser.add_argument("--parameter-file", type=str, required=True, help="Path to the JSON file with runtime parameters")
    parser.add_argument("--service-account", type=str, required=True, help="Service account to run the pipeline job")
    parser.add_argument("--pipeline-root", type=str, required=True, help="GCS URI for the pipeline root directory")
    # Argumenty opcjonalne, zależne od potoku
    parser.add_argument("--gcs-data-path", type=str, help="GCS path to the input data CSV file")
    parser.add_argument("--endpoint-name", type=str, help="Name of the Vertex AI Endpoint")
    parser.add_argument("--model-resource-name", type=str, help="Resource name of the model to deploy")

    args = parser.parse_args()  
    main(args)
