import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    # 1. CREAMOS EL PUENTE: 
    # Tomamos tus variables SP_API_ y las ponemos en las llaves que la librería exige
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
        name = data.get("name", "Developer AMAZON")
        return jsonify({"message": f"Hello {name}!"})

    # GET → Conexión manual forzada
    try:
        # 2. Le pasamos el diccionario directamente al constructor
        sellers_client = Sellers(credentials=credentials, marketplace=Marketplaces.US)
        
        # 3. Llamamos al método correcto (plural)
        response = sellers_client.get_marketplace_participation()
        
        return jsonify({
            "status": "ok",
            "tienda": "Cornilove Store",
            "data": response.payload
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "detalle_tecnico": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
