from flask import Blueprint, request, jsonify
from database import get_db_connection

bicicletas_bp = Blueprint("bicicletas", __name__)


@bicicletas_bp.route("/bicicletas", methods=["POST"])
def cadastrar_bicicleta():
    dados = request.get_json()

    usuario_id = dados.get("usuario_id")
    nome = dados.get("nome")
    marca = dados.get("marca")
    modelo = dados.get("modelo")
    tipo = dados.get("tipo")

    if not usuario_id or not nome:
        return jsonify({
            "erro": "usuario_id e nome são obrigatórios."
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

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO bicicletas (
            usuario_id,
            nome,
            marca,
            modelo,
            tipo
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        usuario_id,
        nome,
        marca,
        modelo,
        tipo
    ))

    connection.commit()

    bicicleta_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "mensagem": "Bicicleta cadastrada com sucesso!",
        "bicicleta": {
            "id": bicicleta_id,
            "usuario_id": usuario_id,
            "nome": nome,
            "marca": marca,
            "modelo": modelo,
            "tipo": tipo
        }
    }), 201


@bicicletas_bp.route("/bicicletas", methods=["GET"])
def listar_bicicletas():
    connection = get_db_connection()

    bicicletas = connection.execute("""
        SELECT
            bicicletas.id,
            bicicletas.nome,
            bicicletas.marca,
            bicicletas.modelo,
            bicicletas.tipo,
            bicicletas.usuario_id,
            usuarios.nome AS usuario_nome
        FROM bicicletas
        JOIN usuarios
            ON bicicletas.usuario_id = usuarios.id
    """).fetchall()

    connection.close()

    resultado = []

    for bicicleta in bicicletas:
        resultado.append({
            "id": bicicleta["id"],
            "nome": bicicleta["nome"],
            "marca": bicicleta["marca"],
            "modelo": bicicleta["modelo"],
            "tipo": bicicleta["tipo"],
            "usuario_id": bicicleta["usuario_id"],
            "usuario_nome": bicicleta["usuario_nome"]
        })

    return jsonify(resultado), 200