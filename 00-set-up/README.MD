## Kroki instalacyjne i uruchomienie

### Wymagania wstępne

* **Konto Google Cloud**: Aktywne konto z uprawnieniami do tworzenia zasobów.
* **Projekt w Google Cloud**: Utworzony nowy projekt z włączonym billingiem.
* **Google Cloud SDK (gcloud)**: Zainstalowane i skonfigurowane na lokalnym komputerze.
* **Terraform**: Zainstalowany w wersji 1.0 lub nowszej.
* **GitHub**: Konto i utworzone repozytorium ze sklonowanym kodem projektu.

### Krok 1: Konfiguracja środowiska lokalnego

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/twoj-login/twoje-repo.git](https://github.com/twoj-login/twoje-repo.git)
    cd twoje-repo
    ```

2.  **Zaloguj się do Google Cloud:**
    ```bash
    gcloud auth login
    gcloud config set project TWOJ_PROJECT_ID
    ```

### Krok 2: Wdrożenie infrastruktury za pomocą Terraform

Wszystkie poniższe komendy wykonuj w folderze `infrastructure/`.

1.  **Skonfiguruj zmienne:**
    Otwórz plik `infrastructure/terraform.tfvars` i ustaw `gcp_project_id`. Możesz również dostosować nazwy bucketów.

2.  **Zainicjalizuj Terraform:**
    Ta komenda pobierze niezbędne wtyczki dostawcy (providers).
    ```bash
    terraform init
    ```

### Krok 3: Bezpośrednie łączenie Cloud Build z Twoim repozytorium GitHub

1.  Przejdź na stronę aplikacji Cloud Build w GitHub Marketplace:
    **[APLIKACJA CLOUD BUILD](https://github.com/marketplace/google-cloud-build)**

2.  Jeśli konfigurujesz aplikację w GitHub po raz pierwszy: Kliknij **Setup with Google Cloud Build** na dole strony. Następnie kliknij **Grant this app access to your GitHub account**.

3.  Jeśli nie jest to Twoja pierwsza konfiguracja aplikacji w GitHub: Kliknij **Configure access**. Otworzy się strona **Applications** Twojego konta osobistego.

4.  Kliknij **Configure** w wierszu Cloud Build.

5.  Wybierz opcję **Only select repositories**, a następnie wybierz repozytorium dla tego projektu.

6.  Kliknij **Save** lub **Install** — etykieta przycisku zmienia się w zależności od Twojego przepływu pracy. Zostaniesz przekierowany do Google Cloud, aby kontynuować instalację.

7.  Zaloguj się na swoje konto Google Cloud. Jeśli pojawi się prośba, autoryzuj integrację Cloud Build z GitHub.

8.  Na stronie **Cloud Build** wybierz swój projekt. Pojawi się kreator.

9.  W sekcji **Wybierz repozytorium** wybierz swoje konto GitHub oraz odpowiednie repozytorium.

10. Jeśli zgadzasz się na warunki, zaznacz pole wyboru, a następnie kliknij **Połącz**.

11. **Połączenie z GitHub zostało ustanowione!** Nie musisz tworzyć triggera w kreatorze.

### Krok 4: Skonfiguruj i wdróż Trigger przez Terraform

1.  **Znajdź identyfikator połączenia**:
    * Przejdź do [konsoli Cloud Build](https://console.cloud.google.com/cloud-build/repositories) i kliknij nazwę swojego połączenia. Skopiuj jego pełny identyfikator z paska adresu lub szczegółów. Będzie on w formacie: `projects/NAZWA-PROJEKTU/locations/REGION/connections/NAZWA-POLACZENIA`.

2.  **Zaktualizuj plik `terraform.tfvars`**:
    * Otwórz plik `infrastructure/terraform.tfvars`.
    * Wklej skopiowany identyfikator do zmiennej `github_connection_id`.
    * Upewnij się, że `github_repo_name` jest poprawnie ustawiony.

3.  **Wdróż Trigger**:
    Uruchom ponownie `terraform apply`. Tym razem Terraform użyje istniejącego połączenia, aby stworzyć w pełni skonfigurowany trigger.
    ```bash
    terraform apply
    ```

### Krok 5: Uruchomienie potoku
