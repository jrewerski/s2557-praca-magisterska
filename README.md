# MLOps - Zautomatyzowany potok trenowania i wdrażania modelu na GCP

## Opis projektu

Ten projekt demonstruje kompletny, zautomatyzowany potok MLOps na platformie Google Cloud Platform (GCP). Celem jest pokazanie, jak połączyć narzędzia takie jak Terraform, Cloud Build, Vertex AI Pipelines i GitHub, aby stworzyć solidne i powtarzalne środowisko do trenowania, oceny i wdrażania modeli uczenia maszynowego.

Projekt został wykonany jako cześć praktyczna pracy magisterskiej na uczelni PJATK. 

---

## Architektura rozwiązania

1.  **Kod źródłowy**: Cały kod, w tym infrastruktura (Terraform), definicje potoków i komponenty, jest przechowywany w repozytorium GitHub.
2.  **Infrastruktura jako kod (IaC)**: Folder `infrastructure/` zawiera kod Terraform, który automatycznie tworzy i zarządza wszystkimi niezbędnymi zasobami w GCP, w tym triggerami Cloud Build.
3.  **Ciągła integracja i dostarczanie (CI/CD)**: Cloud Build jest używany jako narzędzie CI/CD. Dwa triggery są tworzone automatycznie:
    * **Trigger CI**: Uruchamiany po wypchnięciu zmian do gałęzi `main`. Kompiluje oba potoki (treningowy i wdrożeniowy) i uruchamia potok treningowy.
    * **Trigger wdrożeniowy**: Uruchamiany po otrzymaniu wiadomości w temacie Pub/Sub, co dzieje się po pomyślnej rejestracji nowego modelu. Wymaga ręcznego zatwierdzenia.
4.  **Potok treningowy (Vertex AI Pipelines)**: Wykonuje kroki takie jak trenowanie, ewaluacja i warunkowa rejestracja modelu. Jeśli model jest wystarczająco dobry, wysyła powiadomienie do tematu Pub/Sub.
5.  **Potok wdrożeniowy (Vertex AI Pipelines)**: Uruchamiany przez trigger Pub/Sub, wdraża nowo zarejestrowany model na punkcie końcowym (Endpoint) w Vertex AI.

---
Proces konfiguracji i uruchomienie zawarte jest w folderze 00-set-up