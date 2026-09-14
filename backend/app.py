from flask import Flask

from routes.usuarios import usuarios_bp
from routes.bicicletas import bicicletas_bp
from routes.pedaladas import pedaladas_bp

app = Flask(__name__)


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