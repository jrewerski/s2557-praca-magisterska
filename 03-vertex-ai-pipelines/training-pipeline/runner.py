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
import logging

from components.get_data import get_data
from components.preprocess_data import preprocess_data
from components.train_svc_model import train_svc_model
from components.evaluate_svc_model import evaluate_svc_model
from components.get_parent_model import get_parent_model
from components.register_model import register_model
from components.publish_to_pubsub import publish_to_pubsub

PREBUILT_IMAGE_URI = os.environ.get('CUSTOM_COMPONENT_IMAGE_URI')
if PREBUILT_IMAGE_URI:
    get_data.component_spec.implementation.container.image = PREBUILT_IMAGE_URI
    preprocess_data.component_spec.implementation.container.image = PREBUILT_IMAGE_URI
    train_svc_model.component_spec.implementation.container.image = PREBUILT_IMAGE_URI
    evaluate_svc_model.component_spec.implementation.container.image = PREBUILT_IMAGE_URI
    register_model.component_spec.implementation.container.image = PREBUILT_IMAGE_URI
    get_parent_model.component_spec.implementation.container.image = PREBUILT_IMAGE_URI
    publish_to_pubsub.component_spec.implementation.container.image = PREBUILT_IMAGE_URI
# --- Definicja głównego potoku Vertex AI ---
@pipeline(
    name="training-pipeline",
    description="Potok trenujący i rejestrujący model SVC."
)
def training_pipeline(
    gcs_data_path: str = "",
    project_id: str = "",
    region: str = "us-central1",
    model_name: str = "default-model",
    model_labels_str: str = '{}',
    test_split_ratio: float = 0.3,
    min_accuracy_threshold: float = 95.0,
    pubsub_topic_name: str = "model-deployment-topic", 
):
    """Definiuje przepływ pracy w potoku z warunkową rejestracją."""
    get_data_task = get_data(gcs_input_path=gcs_data_path)
    
    transform_data_task = preprocess_data(
        input_data=get_data_task.outputs["input_data"],
        test_split_ratio=test_split_ratio
    )
    
    train_task = train_svc_model(
        train_dataset=transform_data_task.outputs["train_dataset"]
    )
    
    evaluate_task = evaluate_svc_model(
        test_dataset=transform_data_task.outputs["test_dataset"],
        model=train_task.outputs["model"],
    )

    # Warunek: zarejestruj model tylko, jeśli dokładność jest wystarczająco wysoka
    with dsl.If(
        evaluate_task.outputs["accuracy"] >= min_accuracy_threshold,
        name="accuracy-check",
    ):
        get_parent_model_task = get_parent_model(
            project=project_id,
            region=region,
            model_display_name=model_name,
        )
        register_model_task = register_model(
            project_id=project_id,
            region=region,
            model_display_name=model_name,
            model=train_task.outputs["model"],
            parent_model=get_parent_model_task.outputs["parent_model_resource_name"],
            model_labels=model_labels_str
        )
        publish_task = publish_to_pubsub(
            project_id=project_id,
            topic_name=pubsub_topic_name,
            model_resource_name=register_model_task.outputs["model_resource_name"]
        )

if __name__ == '__main__':
    print("Kompilacja potoku")
    compiler.Compiler().compile(
        pipeline_func=training_pipeline,
        package_path="pipeline.json",
    )
