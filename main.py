import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def test_connection():
    if request.method == "POST":
        data = request.json
        name = data.get("name", "Unknown")
        return {"message": f"Hello {name}!"}
    # GET
    try:
        sellers = Sellers(marketplace=Marketplaces.US)
        response = sellers.get_marketplace_participations()
        return jsonify(response.payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run asigna el puerto via variable de entorno
    port = int(os.environ.get("PORT", 8080))
    # Escucha en todas las interfaces
    app.run(host="0.0.0.0", port=port)
