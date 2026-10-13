import os
import secrets
from pathlib import Path
from flask import Flask
from flask_cors import CORS

from routes.usuarios import usuarios_bp
from routes.bicicletas import bicicletas_bp
from routes.pedaladas import pedaladas_bp

app = Flask(__name__)
chave_path = Path(__file__).resolve().parent / ".secret_key"

if not chave_path.exists():
    chave_path.write_text(secrets.token_hex(32))

app.config["SECRET_KEY"] = chave_path.read_text().strip()

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
CORS(
    app,
    resources={
        r"/*": {
            "origins": "http://127.0.0.1:5500"
        }
    },
    supports_credentials=True
)

@app.route("/")
def home():
    return {
        "mensagem": "BikeLog API funcionando!"
    }


app.register_blueprint(usuarios_bp)
app.register_blueprint(bicicletas_bp)
app.register_blueprint(pedaladas_bp)


if __name__ == "__main__":
    app.run(debug=True)