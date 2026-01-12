import os
from flask import Flask, jsonify, request
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

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    creds = get_sp_api_credentials()

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        return jsonify({"message": "Hello Cornilove!", "status": "online"})

    # GET → Prueba en modo SANDBOX (Sin el error de 'is_sandbox')
    try:
        # En Saleweaver, el Sandbox se activa pasando account='sandbox' 
        # o usando credenciales de sandbox específicas.
        sellers_client = Sellers(
            credentials=creds, 
            marketplace=Marketplaces.US,
            account='sandbox'  # <--- Esta es la forma correcta para esta librería
        )
        
        response = sellers_client.get_marketplace_participation()
        
        return jsonify({
            "status": "success_sandbox",
            "message": "Cornilove DB LLC - Conexión de prueba exitosa",
            "data": response.payload
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "detalle_tecnico": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
