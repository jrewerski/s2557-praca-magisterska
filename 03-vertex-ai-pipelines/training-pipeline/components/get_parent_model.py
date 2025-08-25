from kfp.dsl import component, Output, Artifact
from typing import NamedTuple

@component(
    base_image="python:3.9",
    packages_to_install=["google-cloud-aiplatform"]
)
def get_parent_model(
    project: str,
    region: str,
    model_display_name: str,
) -> NamedTuple("Outputs", [("parent_model_resource_name", str)]):

    from google.cloud import aiplatform

    aiplatform.init(project=project, location=region)
    
    # Filtruj modele po nazwie wyświetlanej
    models = aiplatform.Model.list(
        filter=f'display_name="{model_display_name}"'
    )
    
    parent_model_resource_name = ""
    if models:
        # Jeśli model istnieje, pobierz jego pełną nazwę zasobu
        parent_model_resource_name = models[0].resource_name
        print(f"Znaleziono istniejący model: {parent_model_resource_name}")
    else:
        print(f"Nie znaleziono modelu o nazwie: {model_display_name}. Zostanie utworzony nowy wpis.")
        
    return (parent_model_resource_name,)