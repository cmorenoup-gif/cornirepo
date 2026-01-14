# Este archivo permitirá que los reportes pesados de la taza negra se guarden en el Bucket de Iowa.
import os
import json
import logging
from google.cloud import storage

# El nombre de tu bucket de Iowa
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "amazon-cornilove-raw-data")

def upload_to_bucket(data, filename):
    """Guarda los datos en el Cloud Storage para respaldo antes de ir a BigQuery"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)

        # Convertimos la lista de Amazon a formato JSON
        blob.upload_from_string(
            data=json.dumps(data),
            content_type='application/json'
        )
        
        logging.info(f"[STORAGE] Archivo {filename} guardado en el Bucket.")
        return f"gs://{BUCKET_NAME}/{filename}"
    except Exception as e:
        logging.error(f"[STORAGE ERROR] {str(e)}")
        return None
