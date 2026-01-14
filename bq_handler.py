# Este archivo gestiona tus llaves secretas y la conexión a la SP-API.
from google.cloud import bigquery
import logging

PROJECT_ID = "amazon-cornilove"
DATASET_ID = "amz_cornilove"

def auto_insert_to_bq(data, table_id):
    """Inserta datos y crea la tabla automáticamente si no existe"""
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition="WRITE_APPEND",
    )

    if data:
        try:
            load_job = client.load_table_from_json(data, table_ref, job_config=job_config)
            load_job.result()
            return None
        except Exception as e:
            return str(e)
    return "No hay datos para procesar"
