import os
from flask import Flask, jsonify, request
from sp_api.api import Orders
from sp_api.base import Marketplaces, SellingApiException
from google.cloud import bigquery

app = Flask(__name__)

# Configuración de BigQuery para CORNILOVE DB LLC
PROJECT_ID = "amazon-cornilove"
DATASET_ID = "amazon_prueba"  # Actualizado según tu solicitud
TABLE_ID = "orders_test"

def get_sp_api_credentials():
    """Extrae y limpia las credenciales de las variables de entorno"""
    return {
        "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
        "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
        "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
        "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
        "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
        "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
    }

def insert_to_bq(orders):
    """Inserta las órdenes de Amazon en la tabla de BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    rows_to_insert = []
    for order in orders:
        rows_to_insert.append({
            "order_id": order.get("AmazonOrderId"),
            "status": order.get("OrderStatus"),
            "date": order.get("PurchaseDate"),
            "total": float(order.get("OrderTotal", {}).get("Amount", 0.0)),
            "currency": order.get("OrderTotal", {}).get("CurrencyCode", "USD")
        })
    
    if rows_to_insert:
        # insert_rows_json es ideal para streaming directo desde Cloud Run
        errors = client.insert_rows_json(table_ref, rows_to_insert)
        return errors
    return None

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    creds = get_sp_api_credentials()
    
    # Manejo de POST (Prueba de servidor)
    if request.method == "POST":
        return jsonify({"message": "CORNILOVE Server Online", "status": "ok"})

    # Manejo de GET (Extracción y Carga de datos)
    try:
        client = Orders(credentials=creds, marketplace=Marketplaces.US)
        # Consultamos órdenes desde el inicio de 2026
        response = client.get_orders(CreatedAfter="2026-01-01T00:00:00Z")
        orders = response.payload.get("Orders", [])

        # Intentar la inserción en el nuevo dataset 'amazon_prueba'
        bq_errors = insert_to_bq(orders)
        
        if bq_errors:
            return jsonify({
                "status": "error_bq", 
                "mensaje": "Error al insertar en BigQuery",
                "detalle": bq_errors
            }), 500

        return jsonify({
            "status": "ok",
            "mensaje": f"Dataset 'amazon_prueba' actualizado con {len(orders)} órdenes.",
            "orders_count": len(orders)
        })

    except SellingApiException as e:
        return jsonify({"status": "error_amazon", "detalle": str(e)}), 403
    except Exception as e:
        return jsonify({"status": "error_general", "detalle": str(e)}), 500

if __name__ == "__main__":
    # Configuración de puerto para Cloud Run
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
