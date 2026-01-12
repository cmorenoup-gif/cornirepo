import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

def get_sp_api_credentials():
    """Extrae y limpia las credenciales de las variables de entorno de Cloud Run"""
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

    # POST → test de servidor
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Cornilove Developer")
        return jsonify({
            "message": f"Hello {name}!",
            "status": "server_online"
        })

    # GET → conexión a Amazon SP API en Sandbox
    try:
        # Sandbox se activa mediante SP_API_SANDBOX=True
        client = Sellers(credentials=creds, marketplace=Marketplaces.US)
        response = client.get_marketplace_participation()
        
        return jsonify({
            "status": "ok",
            "env_mode": "Sandbox (datos de prueba)",
            "tienda": "Cornilove DB LLC",
            "data": response.payload,
            "nota": "Conexión Sandbox exitosa, no requiere aprobación de app"
        })

    except Exception as e:
        # Manejo de errores
        error_msg = str(e)
        return jsonify({
            "status": "error_autorizacion",
            "mensaje": "Amazon reconoce tus llaves pero la app aún no está aprobada o hay error en Sandbox",
            "detalle_tecnico": error_msg,
            "sugerencia": "Asegúrate de tener SP_API_SANDBOX=True para pruebas o que la app esté aprobada para producción"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
