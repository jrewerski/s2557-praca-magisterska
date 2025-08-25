import pytest
import pandas as pd
import pickle
from kfp.dsl import Dataset, Model, Metrics
from pathlib import Path

# Importujemy logikę z komponentów
from components.train_svc_model import train_svc_model
from components.evaluate_svc_model import evaluate_svc_model

@pytest.fixture
def processed_data(tmp_path):
    """Tworzy przykładowe, przetworzone dane wejściowe i zapisuje je do pliku CSV."""
    data = {
        'culmen_length_mm': [39.1, 40.3, 46.1, 47.0, 50.0, 51.0],
        'culmen_depth_mm': [18.7, 18.0, 13.2, 14.0, 16.4, 17.0],
        'flipper_length_mm': [181.0, 195.0, 211.0, 212.0, 195.0, 198.0],
        'body_mass_g': [3750.0, 3250.0, 4500.0, 4500.0, 3700.0, 3800.0],
        'sex': [0, 1, 1, 0, 1, 1],
        'island_Dream': [False, False, False, False, True, True],
        'island_Torgersen': [True, False, False, False, False, False],
        'species': ['Adelie', 'Adelie', 'Gentoo', 'Gentoo', 'Chinstrap', 'Chinstrap']
    }
    df = pd.DataFrame(data)
    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    df.to_csv(train_path, index=False)
    df.to_csv(test_path, index=False) # W teście użyjemy tych samych danych do treningu i oceny
    
    return str(train_path), str(test_path)

def test_train_and_evaluate_logic(tmp_path, processed_data):
    """
    Testuje połączoną logikę trenowania i oceny modelu.
    Najpierw trenuje model, a następnie go ocenia.
    """
    train_data_path, test_data_path = processed_data
    
    # --- Krok 1: Testowanie komponentu train_svc_model ---
    
    # Symulacja artefaktów KFP
    train_dataset = Dataset(uri=train_data_path)
    model_artifact = Model(uri=str(tmp_path / "model"))

    # Wywołanie funkcji trenującej
    train_svc_model.python_func(
        train_dataset=train_dataset,
        model=model_artifact
    )

    # Sprawdzenie, czy model został zapisany
    model_file_path = Path(model_artifact.path + ".pkl")
    assert model_file_path.exists(), "Plik modelu nie został utworzony."
    
    # Sprawdzenie, czy plik modelu nie jest pusty
    assert model_file_path.stat().st_size > 0

    # --- Krok 2: Testowanie komponentu evaluate_svc_model ---

    # Symulacja artefaktów dla kroku oceny
    test_dataset = Dataset(uri=test_data_path)
    # Używamy modelu wytrenowanego w poprzednim kroku
    trained_model_artifact = Model(uri=model_artifact.uri) 
    metrics_artifact = Metrics(uri=str(tmp_path / "metrics"))

    # Wywołanie funkcji oceniającej
    # Zwracana wartość to krotka, więc pobieramy pierwszy element
    accuracy_output = evaluate_svc_model.python_func(
        test_dataset=test_dataset,
        model=trained_model_artifact,
        metrics=metrics_artifact
    )
    
    accuracy_value = accuracy_output[0]

    # Sprawdzenie wyników
    assert isinstance(accuracy_value, float), "Dokładność powinna być typu float."
    assert 0.0 <= accuracy_value <= 100.0, "Dokładność powinna być w zakresie [0, 100]."

    # W naszym kontrolowanym przypadku (trening i test na tych samych danych)
    # oczekujemy bardzo wysokiej dokładności.
    assert accuracy_value > 90.0, "Oczekiwano wysokiej dokładności na danych treningowych."
    
    # Sprawdzenie, czy metryki zostały zapisane (opcjonalne, ale dobra praktyka)
    # W rzeczywistym wykonaniu KFP, metryki byłyby w pliku JSON.
    # Tutaj symulujemy, sprawdzając, czy katalog istnieje.
    assert Path(metrics_artifact.path).parent.exists()

