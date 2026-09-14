from flask import Blueprint, request, jsonify
from database import get_db_connection

pedaladas_bp = Blueprint("pedaladas", __name__)


@pedaladas_bp.route("/pedaladas", methods=["POST"])
def cadastrar_pedalada():
    dados = request.get_json()

    usuario_id = dados.get("usuario_id")
    bicicleta_id = dados.get("bicicleta_id")
    data = dados.get("data")
    distancia_km = dados.get("distancia_km")
    duracao_minutos = dados.get("duracao_minutos")
    velocidade_media = dados.get("velocidade_media")
    observacoes = dados.get("observacoes")

    if (
        not usuario_id
        or not bicicleta_id
        or not data
        or distancia_km is None
        or duracao_minutos is None
        or velocidade_media is None
    ):
        return jsonify({
            "erro": "Campos obrigatórios não informados."
        }), 400

    connection = get_db_connection()

    usuario = connection.execute("""
        SELECT id
        FROM usuarios
        WHERE id = ?
    """, (usuario_id,)).fetchone()

    if usuario is None:
        connection.close()
        return jsonify({
            "erro": "Usuário não encontrado."
        }), 404

    bicicleta = connection.execute("""
        SELECT id, usuario_id
        FROM bicicletas
        WHERE id = ?
    """, (bicicleta_id,)).fetchone()

    if bicicleta is None:
        connection.close()
        return jsonify({
            "erro": "Bicicleta não encontrada."
        }), 404

    if bicicleta["usuario_id"] != usuario_id:
        connection.close()
        return jsonify({
            "erro": "Essa bicicleta não pertence ao usuário informado."
        }), 400

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO pedaladas (
            usuario_id,
            bicicleta_id,
            data,
            distancia_km,
            duracao_minutos,
            velocidade_media,
            observacoes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        usuario_id,
        bicicleta_id,
        data,
        distancia_km,
        duracao_minutos,
        velocidade_media,
        observacoes
    ))

    connection.commit()

    pedalada_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "mensagem": "Pedalada cadastrada com sucesso!",
        "id": pedalada_id
    }), 201


@pedaladas_bp.route("/pedaladas", methods=["GET"])
def listar_pedaladas():
    connection = get_db_connection()

    pedaladas = connection.execute("""
        SELECT
            pedaladas.id,
            pedaladas.data,
            pedaladas.distancia_km,
            pedaladas.duracao_minutos,
            pedaladas.velocidade_media,
            pedaladas.observacoes,
            pedaladas.usuario_id,
            pedaladas.bicicleta_id,
            usuarios.nome AS usuario_nome,
            bicicletas.nome AS bicicleta_nome
        FROM pedaladas
        JOIN usuarios
            ON pedaladas.usuario_id = usuarios.id
        JOIN bicicletas
            ON pedaladas.bicicleta_id = bicicletas.id
        ORDER BY pedaladas.data DESC
    """).fetchall()

    connection.close()

    resultado = []

    for pedalada in pedaladas:
        resultado.append({
            "id": pedalada["id"],
            "data": pedalada["data"],
            "distancia_km": pedalada["distancia_km"],
            "duracao_minutos": pedalada["duracao_minutos"],
            "velocidade_media": pedalada["velocidade_media"],
            "observacoes": pedalada["observacoes"],
            "usuario": {
                "id": pedalada["usuario_id"],
                "nome": pedalada["usuario_nome"]
            },
            "bicicleta": {
                "id": pedalada["bicicleta_id"],
                "nome": pedalada["bicicleta_nome"]
            }
        })

    return jsonify(resultado), 200