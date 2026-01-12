import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    if request.method == "POST":
        # Endpoint de prueba
        data = request.json
        name = data.get("name", "Developer AMAZON")
        return {"message": f"Hello {name}!"}

    # GET → prueba real de Amazon US SP-API
    try:
        sellers = Sellers()  # crea cliente SP‑API
        response = sellers.get_marketplace_participation()  # método correcto
        return jsonify(response.payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run asigna el puerto via variable de entorno
    port = int(os.environ.get("PORT", 8080))
    # Escucha en todas las interfaces
    app.run(host="0.0.0.0", port=port)
