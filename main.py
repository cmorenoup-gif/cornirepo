import os
import json
from flask import Flask, jsonify
from sp_api.api import Orders
from sp_api.base import Marketplaces, SellingApiException
from google.cloud import bigquery

app = Flask(__name__)

PROJECT_ID = "amazon-cornilove"
DATASET_ID = "amazon_prueba"
TABLE_ID = "orders_dinamica"

def get_sp_api_credentials():
    return {
        "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
        "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
        "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
        "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
        "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
        "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
    }

def auto_insert_to_bq(data):
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    job_config = bigquery.LoadJobConfig(
        autodetect=True, # Crea la tabla y columnas automáticamente
        write_disposition="WRITE_APPEND",
    )

    if data:
        # Forzamos formato JSON serializable para BigQuery
        load_job = client.load_table_from_json(data, table_ref, job_config=job_config)
        load_job.result()
        return None
    return "No data"

@app.route("/", methods=["GET"])
def main_endpoint():
    creds = get_sp_api_credentials()
    try:
        client = Orders(credentials=creds, marketplace=Marketplaces.US)
        response = client.get_orders(CreatedAfter="2026-01-01T00:00:00Z")
        orders = response.payload.get("Orders", [])

        # --- SIMULACIÓN PARA CORNILOVE DB LLC ---
        if not orders:
            print("No hay órdenes reales. Insertando orden de prueba para crear la tabla...")
            orders = [{
                "AmazonOrderId": "TEST-CORNILOVE-001",
                "OrderStatus": "Simulation_Active",
                "PurchaseDate": "2026-01-14T00:00:00Z",
                "OrderTotal": {"Amount": "25.00", "CurrencyCode": "USD"},
                "SalesChannel": "Cornilove_Internal_Test",
                "IsBusinessOrder": "true"
            }]
        # ----------------------------------------

        errors = auto_insert_to_bq(orders)
        
        if errors:
            return jsonify({"status": "error_bq", "detalle": errors}), 500

        return jsonify({
            "status": "ok", 
            "mensaje": "¡Éxito! Tabla creada y datos de prueba insertados en amazon_prueba.",
            "data_source": "Simulation_CORNILOVE" if orders[0]["AmazonOrderId"].startswith("TEST") else "Amazon_Real"
        })

    except SellingApiException as e:
        return jsonify({"status": "error_amazon", "detalle": str(e)}), 403
    except Exception as e:
        return jsonify({"status": "error_general", "detalle": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
