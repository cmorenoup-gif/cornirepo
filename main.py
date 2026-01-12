from flask import Flask, jsonify
from sp_api.api import Sellers
from sp_api.base import Marketplaces
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def test_connection():
    if request.method == "POST":
        data = request.json
        name = data.get("name", "Unknown")
        return {"message": f"Hello {name}!"}
    # GET request
    try:
        sellers = Sellers(marketplace=Marketplaces.US)
        response = sellers.get_marketplace_participations()
        return jsonify(response.payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
