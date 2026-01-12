import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    # 1. Mapeo de credenciales (Cornilove Standard)
    credentials = {
        "refresh_token": os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
        "lwa_app_id": os.getenv('SP_API_CLIENT_ID', '').strip(),
        "lwa_client_secret": os.getenv('SP_API_CLIENT_SECRET', '').strip(),
        "aws_access_key": os.getenv('SP_API_ACCESS_KEY', '').strip(),
        "aws_secret_key": os.getenv('SP_API_SECRET_KEY', '').strip(),
        "role_arn": os.getenv('SP_API_ROLE_ARN', '').strip()
    }

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Cornilove Developer")
        return jsonify({"message": f"Hello {name}!", "status": "server_online"})

    # GET → Prueba en modo SANDBOX
    try:
        # 2. Configuración del cliente con Sandbox activado
        sellers_client = Sellers(
            credentials=credentials, 
            marketplace=Marketplaces.US, 
            account='default',
            is_sandbox=True  # Permite saltar el error 403 mientras esperas aprobación
        )
        
        # 3. Solicitud de datos (singular para tu versión de librería)
        response = sellers_client.get_marketplace_participation()
        
        return jsonify({
            "status": "success_sandbox",
            "message": "Cornilove DB LLC - Conexión de prueba exitosa",
            "data": response.payload
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "detalle_tecnico": str(e),
            "ayuda": "Si el error persiste, verifica que SP_API_CLIENT_ID esté bien mapeado en Cloud Run"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
