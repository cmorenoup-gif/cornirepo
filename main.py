import os
from flask import Flask, jsonify
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

@app.route("/")
def test_connection():
    # 1. Capturamos TODO lo que viene del panel de Cloud Run
    client_id = os.getenv('SP_API_CLIENT_ID', '').strip()
    client_secret = os.getenv('SP_API_CLIENT_SECRET', '').strip()
    r_token = os.getenv('SP_API_REFRESH_TOKEN', '').strip()
    aws_key = os.getenv('SP_API_ACCESS_KEY', '').strip()
    aws_secret = os.getenv('SP_API_SECRET_KEY', '').strip()
    role_arn = os.getenv('SP_API_ROLE_ARN', '').strip()

    # 2. Diagnóstico: Si alguna está vacía, te avisamos de inmediato
    missing = []
    if not client_id: missing.append("SP_API_CLIENT_ID")
    if not client_secret: missing.append("SP_API_CLIENT_SECRET")
    if not r_token: missing.append("SP_API_REFRESH_TOKEN")

    if missing:
        return jsonify({
            "status": "error_configuracion",
            "mensaje": "Google Cloud no esta pasando estas variables al codigo",
            "variables_faltantes": missing
        }), 500

    # 3. Empaquetamos para la librería Saleweaver
    credentials = {
        "refresh_token": r_token,
        "lwa_app_id": client_id,
        "lwa_client_secret": client_secret,
        "aws_access_key": aws_key,
        "aws_secret_key": aws_secret,
        "role_arn": role_arn,
    }

    try:
        sellers = Sellers(credentials=credentials, marketplace=Marketplaces.US)
        response = sellers.get_marketplace_participations()
        return jsonify({"status": "ok", "data": response.payload})
    except Exception as e:
        return jsonify({"status": "error_amazon", "detalle": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
