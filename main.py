import os
import logging
from flask import Flask, jsonify
from amazon_client import AmazonClient
from bq_handler import auto_insert_to_bq
from sp_api.base import SellingApiException

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TABLE_ID = "tbl_sales_all_orders"

@app.route("/", methods=["GET"])
def main_endpoint():
    try:
        # 1. Usar el Mensajero
        amz = AmazonClient()
        orders = amz.fetch_orders()

        # 2. Lógica de Prueba (Sustancia de Negocio)
        if not orders:
            orders = [{
                "AmazonOrderId": "TEST-CORNILOVE-001",
                "OrderStatus": "Simulation_Active",
                "Brand": "Cornilove DB LLC"
            }]

        # 3. Usar el Contador
        errors = auto_insert_to_bq(orders, TABLE_ID)
        
        if errors:
            return jsonify({"status": "error_bq", "detalle": errors}), 500

        logging.info(f"[SUCCESS] {TABLE_ID} actualizado.")
        return jsonify({"status": "ok", "tipo": "Prueba" if "TEST" in orders[0]["AmazonOrderId"] else "Real"})

    except SellingApiException as e:
        return jsonify({"status": "error_amazon", "detalle": str(e)}), 403
    except Exception as e:
        return jsonify({"status": "error_general", "detalle": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
