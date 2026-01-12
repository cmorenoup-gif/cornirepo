from flask import Flask, jsonify
from sp_api.api import Sellers
from sp_api.base import Marketplaces
import os

app = Flask(__name__)

@app.route("/")
def test_connection():
    try:
        sellers = Sellers(marketplace=Marketplaces.US)
        response = sellers.get_marketplace_participations()
        return jsonify(response.payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
