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

# Variable de entorno para activar Sandbox
USE_SANDBOX = os.getenv("USE_SANDBOX", "True").lower() == "true"

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    creds = get_sp_api_credentials()

    # POST → prueba simple de servidor
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Cornilove Developer")
        return jsonify({"message": f"Hello {name}!", "status": "server_online"})

    # GET → Conexión a Amazon SP-API (Sandbox o Producción según USE_SANDBOX)
    try:
        client = Sellers(
            credentials=creds,
            marketplace=Marketplaces.US,
            sandbox=USE_SANDBOX  # <-- aquí activamos Sandbox si corresponde
        )

        response = client.get_marketplace_participation()
        env_mode = "Sandbox (datos de prueba)" if USE_SANDBOX else "Producción (datos reales)"

        return jsonify({
            "status": "ok",
            "tienda": "Cornilove DB LLC",
            "env_mode": env_mode,
            "data": response.payload,
            "nota": "Si ves este mensaje, la conexión con Amazon SP API fue exitosa"
        })

    except Exception as e:
        # Manejo de error: si falla Sellers, posible Draft o problema de credenciales
        error_msg = str(e)
        return jsonify({
            "status": "error_autorizacion",
            "mensaje": "Amazon reconoce tus llaves pero falta aprobación de roles o hay error en Sandbox",
            "detalle_tecnico": error_msg,
            "sugerencia": "Si USE_SANDBOX=True, revisa que la librería SP API soporte Sandbox. Si USE_SANDBOX=False, verifica que el App Status no sea Draft."
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
