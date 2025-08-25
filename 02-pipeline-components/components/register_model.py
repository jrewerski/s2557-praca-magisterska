import kfp
from kfp import dsl
from kfp.dsl import (Artifact,
                        Dataset,
                        Input,
                        InputPath,
                        Output,
                        OutputPath,
                        component,
                        Model
                        )
import json


@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "google-cloud-aiplatform==1.55.0", "gcsfs==2024.6.0", "fsspec", "pyarrow", "scikit-learn==1.5.0"],
)
def register_model(
    model: Input[Model],
    project_id: str,
    region: str,
    model_display_name: str,
    parent_model: str = "" ,
    model_labels: str = '{}'
):
    """Rejestruje model w Vertex AI Model Registry."""
    from google.cloud import aiplatform
    import json

    print(f"project_id : {project_id}")
    print(f"region : {region}")
    print(f"model : {model}")

    aiplatform.init(project=project_id, location=region)

    try:
        labels = json.loads(model_labels)
        print(f"Używam etykiet: {labels}")
    except json.JSONDecodeError:
            print("Błąd w parsowaniu etykiet.")

    serving_container_image = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-5:latest"
    model_path = '/'.join(model.uri.split('/')[:-1])
    # Przesłanie i rejestracja modelu
    registered_model = aiplatform.Model.upload(
        display_name=model_display_name,
        artifact_uri=model_path,
        serving_container_image_uri=serving_container_image,
        sync=True,
        parent_model=parent_model,
        labels = {"model_type": "svc", "framework" : "scikit-learn"}
    )
    print(f"Zarejestrowano model: {registered_model.resource_name}")