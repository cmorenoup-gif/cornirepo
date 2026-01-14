import os
import logging
import requests
import time
from flask import Flask, jsonify
from amazon_client import AmazonClient
from bq_handler import auto_insert_to_bq
from storage_manager import upload_to_bucket
from sp_api.base import SellingApiException

# --- IMPORTANTE: Integración de Alertas de Cornilove ---
from notifications import send_critical_alert 

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuración de tablas según tu DISEÑO ESTABLE
REPORTS_CONFIG = {
    "inventory": "tbl_inventory_ledger",
    "fba_stock": "tbl_fba_logistics",
    "orders": "tbl_sales_all_orders",
    "ads": "tbl_marketing_ads"
}

@app.route("/sync-report/<report_name>", methods=["GET"])
def sync_amazon_report(report_name):
    """
    Ruta maestra: Pide a Amazon -> Descarga Contenido -> Guarda en Bucket -> BigQuery
    """
    try:
        amz = AmazonClient()
        
        # 1. Mapeo de códigos técnicos de tu Excel
        report_types = {
            "inventory": "GET_LEDGER_SUMMARY_VIEW_DATA",
            "fba_stock": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
            "orders": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
            "ads": "GET_ADVERTISING_PROMOTIONS_REPORT"
        }
        
        type_code = report_types.get(report_name)
        if not type_code:
            return jsonify({"status": "error", "message": "Reporte no configurado"}), 400

        # 2. Solicitar y esperar reporte (Polling)
        report_url = amz.get_report(type_code)
        
        if not report_url:
            # --- SE DISPARA LA ALERTA AQUÍ ---
            error_msg = "Amazon no generó el reporte a tiempo"
            send_critical_alert(error_msg, report_name=report_name)
            return jsonify({"status": "error", "message": error_msg}), 500

        # 3. DESCARGA REAL del contenido desde Amazon
        logging.info(f"[DESCARGA] Bajando contenido desde URL de Amazon para {report_name}")
        response = requests.get(report_url)
        report_content = response.text # Contenido crudo (CSV/TSV)

        # 4. ALMACÉN: Guardar archivo crudo en el Bucket de Iowa
        timestamp = int(time.time())
        file_name = f"{report_name}_{timestamp}.csv"
        gcs_path = upload_to_bucket(report_content, file_name)

        # 5. CONTADOR: Ingesta en BigQuery
        table_id = REPORTS_CONFIG.get(report_name)
        bq_error = auto_insert_to_bq([{"raw_data": report_content[:1000], "source": file_name}], table_id)

        if bq_error:
            logging.error(f"[BQ ERROR] {bq_error}")
            # Opcional: Podrías enviar alerta aquí también si falla la base de datos

        return jsonify({
            "status": "ok",
            "empresa": "Cornilove DB LLC",
            "reporte": report_name,
            "archivo_gcs": gcs_path,
            "tabla_bq": table_id
        })

    except Exception as e:
        error_general = str(e)
        logging.error(f"Error en flujo {report_name}: {error_general}")
        # --- ALERTA PARA CUALQUIER OTRO FALLO TÉCNICO ---
        send_critical_alert(f"Error General: {error_general}", report_name=report_name)
        return jsonify({"status": "error_general", "detalle": error_general}), 500

@app.route("/", methods=["GET"])
def health_check():
    """Señal de vida para Uptime Check"""
    return jsonify({"status": "active", "empresa": "Cornilove DB LLC"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
