import kfp
from kfp import dsl
from kfp.dsl import (Artifact,
                        Dataset,
                        Input,
                        InputPath,
                        Output,
                        OutputPath,
                        component
                        )
@component(
    packages_to_install=["pandas==2.2.2", "gcsfs", "fsspec", "pyarrow"],
    base_image="python:3.9"
)
def get_data(gcs_input_path: str
            , input_data : Output[Dataset]):

    import pandas as pd 
    #wczytanie danych
    df = pd.read_csv(gcs_input_path)
    df.to_csv(input_data.path, index=False)