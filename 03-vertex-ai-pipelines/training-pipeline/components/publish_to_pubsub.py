import json
import sys
from kfp.dsl import component

@component(
    base_image="python:3.9",
    packages_to_install=["google-cloud-pubsub==2.13.4"]
)
def publish_to_pubsub(
    project_id: str,
    topic_name: str,
    model_resource_name: str,
):
    """
    Publikuje wiadomość z atrybutem zawierającym ID modelu do określonego  Pub/Sub.
    """
    from google.cloud import pubsub_v1

    try:
        model_id = model_resource_name.split('/')[-1]
        print(f"ID modelu: {model_id}")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)

        # Wiadomość może mieć pustą treść, ponieważ kluczowe dane
        # przekazujemy jako atrybut.
        data = b"" 
        
        print(f"Publikowanie wiadomości do tematu {topic_path} z atrybutem...")
        
        # Przekazujemy ID modelu jako atrybut wiadomości.
        # Klucz atrybutu ("model_resource_name") musi być taki sam,
        # jak ten użyty w konfiguracji triggera Cloud Build.
        future = publisher.publish(
            topic_path,
            data,
            model_resource_name=model_id
        )
        
        # Czekamy na pomyślne opublikowanie i pobieramy ID wiadomości
        message_id = future.result()
        print(f"Wiadomość opublikowana pomyślnie. ID wiadomości: {message_id}")

    except Exception as e:
        print(f"Wystąpił błąd podczas publikowania wiadomości: {e}", file=sys.stderr)
        sys.exit(1)