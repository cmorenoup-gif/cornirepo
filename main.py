import os
from flask import Flask, jsonify, request
from sp_api.api import Sellers

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main_endpoint():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "Developer AMAZON")
        return jsonify({"message": f"Hello {name}!"})

    # GET → La librería ahora busca las variables SP_API_ automáticamente
    try:
        # Al no pasarle argumentos, Sellers() busca SP_API_CLIENT_ID, etc. en el entorno
        sellers_client = Sellers() 
        
        # Método correcto según el commit y la documentación
        response = sellers_client.get_marketplace_participations()
        
        return jsonify({
            "status": "ok",
            "info": "Validado con el estándar Saleweaver",
            "data": response.payload
        })
    except Exception as e:
        # Si sigue fallando, este error nos dirá qué variable específica no encontró la librería
        return jsonify({
            "status": "error",
            "detalle_tecnico": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
