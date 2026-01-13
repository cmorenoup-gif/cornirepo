import os
import csv
import requests
from io import StringIO
from flask import Flask, jsonify
from sp_api.api import Reports
from sp_api.base import Marketplaces, SellingApiException
from google.cloud import bigquery

app = Flask(__name__)

# Dataset y tabla en BigQuery
BQ_DATASET = "amazon_reports"
BQ_TABLE = "orders_test"

def get_sp_api_credentials():
    """Extrae y limpia las credenciales de SP-API desde variables de entorno"""
    return {
        "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
        "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
        "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
        "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
        "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
        "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
    }

def insert_rows_to_bigquery(rows, schema):
    """Inserta filas en BigQuery"""
    client = bigquery.Client()
    table_ref = f"{client.project}.{BQ_DATASET}.{BQ_TABLE}"

    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        print("Errores al insertar en BigQuery:", errors)
        return False
    return True

@app.route("/test-report", methods=["GET"])
def generate_test_report():
    creds = get_sp_api_credentials()

    try:
        # 1️⃣ Crear un reporte de órdenes
        reports_client = Reports(credentials=creds)
        report_response = reports_client.create_report(
            reportType="GET_FLAT_FILE_ORDERS_DATA",  # reporte de prueba
            dataStartTime="2026-01-01T00:00:00Z",
            dataEndTime="2026-01-13T23:59:59Z",
            marketplaceIds=[Marketplaces.US.marketplace_id]
        )
        report_id = report_response.payload["reportId"]

        # 2️⃣ Esperar a que esté listo (polling simple)
        status = ""
        while status not in ["DONE", "CANCELLED", "FATAL"]:
            report_status = reports_client.get_report(report_id).payload
            status = report_status["processingStatus"]

        if status != "DONE":
            return jsonify({
                "status": "error",
                "mensaje": f"Reporte no completado, status: {status}"
            }), 500

        # 3️⃣ Obtener el documento
        report_doc = reports_client.get_report_document(report_id).payload
        download_url = report_doc["url"]

        # 4️⃣ Descargar CSV
        response = requests.get(download_url)
        response.raise_for_status()
        csv_content = response.content.decode("utf-8")

        # 5️⃣ Parsear CSV
        f = StringIO(csv_content)
        reader = csv.DictReader(f)
        rows = [row for row in reader]

        if not rows:
            return jsonify({
                "status": "ok",
                "mensaje": "Reporte descargado pero no hay datos (esperado si tienda está vacía)"
            })

        # 6️⃣ Insertar en BigQuery
        success = insert_rows_to_bigquery(rows, reader.fieldnames)
        if not success:
            return jsonify({
                "status": "error",
                "mensaje": "No se pudieron insertar filas en BigQuery"
            }), 500

        return jsonify({
            "status": "ok",
            "mensaje": f"Reporte insertado correctamente en {BQ_DATASET}.{BQ_TABLE}",
            "rows_count": len(rows)
        })

    except SellingApiException as e:
        code = getattr(e, "code", None)
        if code in ["Unauthorized", "AccessDenied"]:
            return jsonify({
                "status": "error_autorizacion",
                "mensaje": "El refresh token no tiene el rol 'Inventory and Order Tracking' autorizado"
            }), 403
        return jsonify({"status": "error_tecnico", "detalle_tecnico": str(e)}), 500

    except Exception as e:
        return jsonify({"status": "error_desconocido", "detalle_tecnico": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
