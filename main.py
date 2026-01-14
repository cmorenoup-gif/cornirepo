from storage_manager import upload_to_bucket
from bq_handler import auto_insert_to_bq
from amazon_client import AmazonClient

@app.route("/reporte-inventario", methods=["GET"])
def sync_inventory():
    amz = AmazonClient()
    # 1. Pedir a Amazon el Inventory Ledger
    report_url = amz.get_report("GET_LEDGER_SUMMARY_VIEW_DATA")
    
    if report_url:
        # En la vida real, aquí descargarías el contenido del URL.
        # Por ahora, simulamos el flujo de éxito:
        data = [{"sku": "TAZA-NEGRA-01", "stock": 100, "velocidad": "alta"}]
        
        # 2. Respaldar en Bucket de Iowa
        upload_to_bucket(data, "inventario_mayo.json")
        
        # 3. Meter a BigQuery
        auto_insert_to_bq(data, "tbl_inventory_ledger")
        
        return jsonify({"status": "ok", "mensaje": "Inventario actualizado"})
    return jsonify({"status": "error", "mensaje": "Amazon no generó el reporte"}), 500
