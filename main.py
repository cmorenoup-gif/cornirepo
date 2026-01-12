import os
from flask import Flask, jsonify
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

def get_sp_api_credentials():
    return {
        "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
        "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
        "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
        "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
        "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
        "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
    }

@app.route("/", methods=["GET"])
def main_endpoint():
    creds = get_sp_api_credentials()
    try:
        # Sandbox se activa mediante SP_API_SANDBOX=True
        client = Sellers(credentials=creds, marketplace=Marketplaces.US)
        response = client.get_marketplace_participation()
        return jsonify({
            "status": "ok",
            "env_mode": "Sandbox",
            "data": response.payload
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "detalle_tecnico": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
