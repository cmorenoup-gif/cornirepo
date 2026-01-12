import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers
from sp_api.base import Marketplaces

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    # Mapeo de credenciales desde Secret Manager (Nombres Saleweaver)
    credentials = dict(
        refresh_token=os.getenv('SP_API_REFRESH_TOKEN', '').strip(),
        lwa_app_id=os.getenv('SP_API_CLIENT_ID', '').strip(),
        lwa_client_secret=os.getenv('SP_API_CLIENT_SECRET', '').strip(),
        aws_access_key=os.getenv('SP_API_ACCESS_KEY', '').strip(),
        aws_secret_key=os.getenv('SP_API_SECRET_KEY', '').strip(),
        role_arn=os.getenv('SP_API_ROLE_ARN', '').strip()
    )

    if request.method == "POST":
        # Mantenemos tu lógica original de POST
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Developer AMAZON")
        return jsonify({"message": f"Hello {name}!"})

    # GET → prueba real de Amazon US SP-API
    try:
        # 1. Verificamos que no falten credenciales críticas
        if not credentials['lwa_app_id'] or not credentials['refresh_token']:
            return jsonify({"error": "Faltan variables SP_API_ en el panel de Cloud Run"}), 500

        # 2. Creamos el cliente con tus credenciales de Cornilove
        sellers_client = Sellers(credentials=credentials, marketplace=Marketplaces.US)
        
        # 3. Llamamos al método correcto (plural)
        response = sellers_client.get_marketplace_participations()
        
        return jsonify({
            "status": "ok",
            "tienda": "Cornilove Store",
            "data": response.payload
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
