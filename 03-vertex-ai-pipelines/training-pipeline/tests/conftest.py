import sys
from pathlib import Path

# Ten plik jest automatycznie wykonywany przez pytest przed uruchomieniem testów.
# Dodajemy katalog nadrzędny (w tym przypadku 'training-pipeline') do ścieżki systemowej.
# Dzięki temu importy takie jak 'from components.preprocess_data' będą działać poprawnie
# w plikach testowych.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
