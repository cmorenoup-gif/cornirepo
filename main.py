import os
from flask import Flask, jsonify, request
from sp_api.api import Orders
from sp_api.base import Marketplaces, SellingApiException

app = Flask(__name__)

def get_sp_api_credentials():
    """Extrae y limpia las credenciales de las variables de entorno"""
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
        name = data.get("name", "Cornilove Developer").strip()
        return jsonify({"message": f"Hello {name}!", "status": "server_online"})

    # GET → Intentamos acceder a Orders API para validar Inventory and Order Tracking
    try:
        client = Orders(credentials=creds, marketplace=Marketplaces.US)
        response = client.get_orders(CreatedAfter="2026-01-01T00:00:00Z")  # Solo prueba, no importa fecha exacta

        return jsonify({
            "status": "ok",
            "mensaje": "Token autorizado para Inventory and Order Tracking",
            "orders_count": len(response.payload.get("Orders", [])),
            "nota": "Si ves esto, tu refresh token tiene acceso al rol requerido"
        })

    except SellingApiException as e:
        error_code = getattr(e, 'code', None)
        error_msg = getattr(e, 'message', str(e))

        if error_code in ["Unauthorized", "AccessDenied"]:
            return jsonify({
                "status": "error_autorizacion",
                "mensaje": "El refresh token no tiene el rol 'Inventory and Order Tracking' autorizado",
                "sugerencia": (
                    "1. Ve a Solution Provider Portal.\n"
                    "2. Confirma que tu Developer Profile tiene el rol 'Inventory and Order Tracking'.\n"
                    "3. Haz self-authorization para tu cuenta Seller y usa el refresh token resultante."
                )
            }), 403

        return jsonify({
            "status": "error_tecnico",
            "mensaje": "Ocurrió un error al conectar con SP-API",
            "detalle_tecnico": error_msg
        }), 500

    except Exception as e:
        return jsonify({
            "status": "error_desconocido",
            "mensaje": "Error inesperado en el servidor",
            "detalle_tecnico": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
