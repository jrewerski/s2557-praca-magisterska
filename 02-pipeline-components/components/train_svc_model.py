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

@component(
    base_image="python:3.9",
    packages_to_install=["kfp" ,"pandas==2.2.2", "pyarrow", "scikit-learn==1.5.0", "gcsfs==2024.6.0", "fsspec", "click==8.1.7", "docstring-parser==0.16", "urllib3", "protobuf"]
)
def train_svc_model(
    train_dataset: Input[Dataset],
    model: Output[Model],
):
    """Trenuje klasyfikator SVC i zapisuje model."""
    import pandas as pd
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    import pickle

    print(f"train_data : {train_dataset}")
    print(f"model : {model}")
    train_df = pd.read_csv(train_dataset.path)
    X_train = train_df.drop('species', axis=1)
    y_train = train_df['species']
    svc_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('svc', SVC(kernel='rbf', probability=True, random_state=42))
    ])
    svc_pipeline.fit(X_train, y_train)

    file_name = model.path + f".pkl"
    with open(file_name, 'wb') as file:  
        pickle.dump(svc_pipeline, file)
