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
    packages_to_install=["pandas==2.2.2", "scikit-learn==1.5.0", "pyarrow"],
    base_image="python:3.9"
)
def preprocess_data(
    input_data: Input[Dataset],
    train_dataset: Output[Dataset],
    test_dataset: Output[Dataset],
    test_split_ratio: float,
):

    import pandas as pd
    from sklearn.model_selection import train_test_split
    pd.options.mode.chained_assignment = None

    """Czyści, imputuje, dzieli i zapisuje dane jako artefakty treningowe/testowe."""

    df = pd.read_csv(input_data.path)
    df.loc[336, 'sex'] = 'FEMALE'
    numerical_cols = ['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 'body_mass_g']
    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())
    df['sex'] = df['sex'].fillna(df['sex'].mode()[0])
    df['sex'] = df['sex'].map({'MALE': 0, 'FEMALE': 1})
    df_processed = pd.get_dummies(df, columns=['island'], drop_first=True)
    X = df_processed.drop('species', axis=1)
    y = df_processed['species']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_split_ratio, random_state=42, stratify=y)
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    # zapis do artefaktów: 
    train_df.to_csv(train_dataset.path, index=False)
    test_df.to_csv(test_dataset.path, index=False)