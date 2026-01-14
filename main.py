import os
import logging
from flask import Flask, jsonify
from amazon_client import AmazonClient
from bq_handler import auto_insert_to_bq
from storage_manager import upload_to_bucket
from sp_api.base import SellingApiException

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuración de tablas según tu Excel de reportes
REPORTS_CONFIG = {
    "inventory": "tbl_inventory_ledger",
    "fba_stock": "tbl_fba_inventory",
    "orders": "tbl_sales_all_orders"
}

@app.route("/sync-report/<report_name>", methods=["GET"])
def sync_amazon_report(report_name):
    """
    Ruta unificada para procesar reportes: 
    Pide a Amazon -> Guarda en Bucket -> Inserta en BigQuery
    """
    try:
        amz = AmazonClient()
        
        # 1. Mapeo del reporte según tu Excel
        report_types = {
            "inventory": "GET_LEDGER_SUMMARY_VIEW_DATA",
            "fba_stock": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
            "orders": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
        }
        
        type_code = report_types.get(report_name)
        if not type_code:
            return jsonify({"status": "error", "message": "Reporte no configurado"}), 400

        # 2. El Mensajero pide el reporte (usa la nueva función de polling)
        report_url = amz.get_report(type_code)
        
        if not report_url:
            return jsonify({"status": "error", "message": "Amazon no generó el reporte"}), 500

        # 3. Datos de Simulación (Mientras la taza negra llega al almacén)
        # En producción, aquí descargarías el contenido del report_url
        simulated_data = [{
            "report_type": report_name,
            "status": "Verified",
            "sku": "CORNILOVE-MUG-BLACK",
            "brand": "Cornilove DB LLC"
        }]

        # 4. El Almacén guarda el respaldo en Iowa
        file_name = f"backup_{report_name}_2026.json"
        gcs_path = upload_to_bucket(simulated_data, file_name)

        # 5. El Contador lo registra en BigQuery
        table_id = REPORTS_CONFIG.get(report_name)
        bq_error = auto_insert_to_bq(simulated_data, table_id)

        if bq_error:
            return jsonify({"status": "error_bq", "detalle": bq_error}), 500

        return jsonify({
            "status": "ok",
            "reporte": report_name,
            "storage_path": gcs_path,
            "database_table": table_id
        })

    except Exception as e:
        logging.error(f"Error en flujo de reporte: {str(e)}")
        return jsonify({"status": "error_general", "detalle": str(e)}), 500

# Mantenemos tu ruta original para órdenes rápidas
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "active", "empresa": "Cornilove DB LLC"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
