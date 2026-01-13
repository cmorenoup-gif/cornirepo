import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces, SellingApiException

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

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Cornilove Developer").strip()
        return jsonify({"message": f"Hello {name}!", "status": "server_online"})

    # GET → Conexión a Amazon SP-API
    try:
        client = Sellers(credentials=creds, marketplace=Marketplaces.US)
        response = client.get_marketplace_participation()

        return jsonify({
            "status": "ok",
            "tienda": "Cornilove DB LLC",
            "data": response.payload,
            "nota": "Si ves este mensaje, Amazon ya aprobó tus roles de Sellers y la app está autorizada"
        })

    except SellingApiException as e:
        # Manejo inteligente de errores de SP-API
        error_code = getattr(e, 'code', None)
        error_msg = getattr(e, 'message', str(e))

        if error_code in ["Unauthorized", "AccessDenied"]:
            # Mensaje amigable si el token no tiene los roles correctos
            return jsonify({
                "status": "error_autorizacion",
                "mensaje": "El refresh token no tiene los roles necesarios o no se ha hecho self-authorization",
                "sugerencia": (
                    "1. Revisa tu Developer Profile en Solution Provider Portal.\n"
                    "2. Asegúrate de que los roles requeridos estén aprobados (Selling Partner Insights, Orders, etc.).\n"
                    "3. Haz self-authorization de la app para tu cuenta Seller y usa el refresh token resultante."
                )
            }), 403

        # Otros errores
        return jsonify({
            "status": "error_tecnico",
            "mensaje": "Ocurrió un error al conectar con SP-API",
            "detalle_tecnico": error_msg
        }), 500

    except Exception as e:
        # Captura cualquier otra excepción inesperada
        return jsonify({
            "status": "error_desconocido",
            "mensaje": "Error inesperado en el servidor",
            "detalle_tecnico": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
