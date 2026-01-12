import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

def get_sp_api_credentials():
    """Obtiene las credenciales de Amazon SP API desde variables de entorno."""
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

    # POST → prueba simple
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Developer AMAZON")
        return jsonify({
            "message": f"Hello {name}!",
            "status": "online"
        })

    # GET → prueba Sandbox
    try:
        sellers_client = Sellers(
            **creds,
            marketplace=Marketplaces.US,
            sandbox=True  # <-- activa Sandbox
        )

        response = sellers_client.get_marketplace_participation()

        return jsonify({
            "status": "success_sandbox",
            "message": "Conexión de prueba a Sandbox exitosa",
            "data": response.payload
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "detalle_tecnico": str(e)
        }), 500

if __name__ == "__main__":
    # Cloud Run define el puerto por la variable PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
