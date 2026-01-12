import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers, Orders
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

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Cornilove Developer")
        return jsonify({"message": f"Hello {name}!", "status": "server_online"})

    # GET → Conexión a Amazon SP-API
    try:
        # Usamos Sellers para verificar participación (lo que daba 403)
        # Nota: Si sigue dando 403, es por la aprobación pendiente de Amazon
        client = Sellers(credentials=creds, marketplace=Marketplaces.US)
        response = client.get_marketplace_participation()
        
        return jsonify({
            "status": "ok",
            "tienda": "Cornilove DB LLC",
            "data": response.payload,
            "nota": "Si ves este mensaje, Amazon ya aprobó tus roles de Sellers"
        })

    except Exception as e:
        # Diagnóstico inteligente: si falla Sellers, intentamos confirmar si la conexión base sirve
        error_msg = str(e)
        return jsonify({
            "status": "error_autorizacion",
            "mensaje": "Amazon reconoce tus llaves pero falta aprobacion de roles",
            "detalle_tecnico": error_msg,
            "sugerencia": "Verifica que el App Status en Seller Central no sea Draft"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
