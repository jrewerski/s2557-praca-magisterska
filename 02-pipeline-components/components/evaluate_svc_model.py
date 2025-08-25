import kfp
from kfp import dsl
from kfp.dsl import (Artifact,
                        Dataset,
                        Input,
                        InputPath,
                        Output,
                        OutputPath,
                        component,
                        Model,
                        Metrics
                        )
from typing import NamedTuple

@component(
    base_image="python:3.9",
    packages_to_install=["pandas==2.2.2", "scikit-learn==1.5.0", "gcsfs==2024.6.0", "fsspec"],
)
def evaluate_svc_model(
    test_dataset: Input[Dataset],
    model: Input[Model],
    metrics: Output[Metrics],
) -> NamedTuple("Outputs", [("accuracy", float)]):
    """Ocenia model, zapisuje metryki i zwraca dokładność."""
    import pandas as pd
    from sklearn.metrics import accuracy_score, classification_report
    import pickle 

    print(f"model.path : {model.path}")
    file_name = model.path + f".pkl"
    print(f"file_name : {file_name}")
    
    with open(file_name, 'rb') as file:  
        model = pickle.load(file)

    test_df = pd.read_csv(test_dataset.path)
    X_test = test_df.drop('species', axis=1)
    y_test = test_df['species']
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    metrics.log_metric("accuracy", (accuracy * 100.0))
    print(f"Accuracy: {accuracy}")

    report = classification_report(y_test, y_pred, output_dict=True)
        
    for class_label, class_metrics in report.items():
        if isinstance(class_metrics, dict):
            for metric_name, metric_value in class_metrics.items():
                metrics.log_metric(f"{class_label}_{metric_name}", metric_value)
    
    return (accuracy * 100.0,)