import os
import kfp
from kfp import dsl
from kfp.dsl import (Artifact,
                        Dataset,
                        Input,
                        InputPath,
                        Model,
                        Output,
                        OutputPath,
                        component,
                        Metrics,
                        pipeline)
from kfp import compiler
from google.cloud import aiplatform
from typing import NamedTuple
from google_cloud_pipeline_components.v1.model import ModelGetOp
from google_cloud_pipeline_components.v1.endpoint import ModelDeployOp

@component(
    base_image="python:3.9",
    # Upewnij się, że wersja jest zgodna z tą w Twoim środowisku
    packages_to_install=["google-cloud-aiplatform==1.55.0"] 
)
def get_or_create_endpoint(
    project: str,
    location: str,
    display_name: str,
    endpoint: Output[Artifact], # Komponent zwraca artefakt typu Endpoint
):
    """
    Sprawdza, czy endpoint o podanej nazwie istnieje. Jeśli tak, używa go.
    Jeśli nie, tworzy nowy.
    """
    import logging
    from google.cloud import aiplatform
    
    logging.getLogger().setLevel(logging.INFO)
    aiplatform.init(project=project, location=location)

    # Szukamy istniejącego endpointu
    endpoints = aiplatform.Endpoint.list(
        filter=f'display_name="{display_name}"',
        order_by="create_time desc"
    )

    if endpoints:
        endpoint_resource = endpoints[0]
        logging.info(f"Endpoint '{display_name}' już istnieje. Używam: {endpoint_resource.resource_name}")
    else:
        logging.info(f"Endpoint '{display_name}' nie został znaleziony. Tworzę nowy.")
        endpoint_resource = aiplatform.Endpoint.create(display_name=display_name)

    # Zapisujemy metadane artefaktu, aby kolejne kroki mogły go użyć
    endpoint.uri = f"https://{location}-aiplatform.googleapis.com/v1/{endpoint_resource.resource_name}"
    endpoint.metadata["resourceName"] = endpoint_resource.resource_name


@pipeline(
    name="deployment-pipeline",
    description="Potok tworzy endpoint i wdraża na nim podany model",
    pipeline_root="gs://vertex-ai-bucket-s25537/deployment-pipeline",
)
def deployment_pipeline(
    endpoint_name: str,
    model_resource_name: str,
    project_id: str = "mlops-on-gcp-s25537",
    region: str = "us-central1",
):
    """
    Znajduje istniejący endpoint o podanej nazwie lub tworzy nowy,
    a następnie wdraża na nim podany model.
    """
    get_or_create_endpoint_task = get_or_create_endpoint(
        project = project_id,
        location = region,
        display_name = endpoint_name
    )

    get_model_op = ModelGetOp(
        model_name=model_resource_name,
        location = region
    )

    model_deploy = ModelDeployOp(
        model=get_model_op.outputs["model"],
        endpoint = get_or_create_endpoint_task.outputs["endpoint"],
        deployed_model_display_name = "Predict-svg", 
        dedicated_resources_machine_type="n1-standard-2",
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1
    )


if __name__ == '__main__':
    print("Kompilacja potoku")
    compiler.Compiler().compile(
        pipeline_func=deployment_pipeline,
        package_path="pipeline.json",
    )
