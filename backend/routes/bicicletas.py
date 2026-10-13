
from flask import Blueprint, request, jsonify, session
from database import get_db_connection

bicicletas_bp = Blueprint("bicicletas", __name__)


# CADASTRAR BICICLETA
@bicicletas_bp.route("/bicicletas", methods=["POST"])
def cadastrar_bicicleta():

    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome")
    marca = dados.get("marca")
    modelo = dados.get("modelo")
    tipo = dados.get("tipo")

    if not isinstance(nome, str) or not nome.strip():
        return jsonify({
            "erro": "O nome da bicicleta é obrigatório."
        }), 400

    nome = nome.strip()

    connection = get_db_connection()
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


# LISTAR BICICLETAS DO USUÁRIO LOGADO
@bicicletas_bp.route("/bicicletas", methods=["GET"])
def listar_bicicletas():

    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    connection = get_db_connection()

    bicicletas = connection.execute("""
        SELECT
            id,
            usuario_id,
            nome,
            marca,
            modelo,
            tipo
        FROM bicicletas
        WHERE usuario_id = ?
        ORDER BY id DESC
    """, (usuario_id,)).fetchall()

    connection.close()

    resultado = []

    for bicicleta in bicicletas:
        resultado.append({
            "id": bicicleta["id"],
            "usuario_id": bicicleta["usuario_id"],
            "nome": bicicleta["nome"],
            "marca": bicicleta["marca"],
            "modelo": bicicleta["modelo"],
            "tipo": bicicleta["tipo"]
        })

    return jsonify(resultado), 200

# EDITAR BICICLETA
@bicicletas_bp.route("/bicicletas/<int:bicicleta_id>", methods=["PUT"])
def editar_bicicleta(bicicleta_id):

    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome")
    marca = dados.get("marca")
    modelo = dados.get("modelo")
    tipo = dados.get("tipo")

    if not isinstance(nome, str) or not nome.strip():
        return jsonify({
            "erro": "O nome da bicicleta é obrigatório."
        }), 400

    nome = nome.strip()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE bicicletas
        SET
            nome = ?,
            marca = ?,
            modelo = ?,
            tipo = ?
        WHERE id = ?
        AND usuario_id = ?
    """, (
        nome,
        marca,
        modelo,
        tipo,
        bicicleta_id,
        usuario_id
    ))

    if cursor.rowcount == 0:
        connection.close()
        return jsonify({
            "erro": "Bicicleta não encontrada."
        }), 404

    connection.commit()
    connection.close()

    return jsonify({
        "mensagem": "Bicicleta atualizada com sucesso!",
        "bicicleta": {
            "id": bicicleta_id,
            "usuario_id": usuario_id,
            "nome": nome,
            "marca": marca,
            "modelo": modelo,
            "tipo": tipo
        }
    }), 200

# EXCLUIR BICICLETA
@bicicletas_bp.route("/bicicletas/<int:bicicleta_id>", methods=["DELETE"])
def excluir_bicicleta(bicicleta_id):

    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    connection = get_db_connection()

    bicicleta = connection.execute("""
        SELECT id
        FROM bicicletas
        WHERE id = ? AND usuario_id = ?
    """, (bicicleta_id, usuario_id)).fetchone()

    if bicicleta is None:
        connection.close()
        return jsonify({
            "erro": "Bicicleta não encontrada."
        }), 404

    pedalada = connection.execute("""
        SELECT id
        FROM pedaladas
        WHERE bicicleta_id = ?
        LIMIT 1
    """, (bicicleta_id,)).fetchone()

    if pedalada is not None:
        connection.close()
        return jsonify({
            "erro": "Não é possível excluir uma bicicleta com pedaladas registradas."
        }), 409

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM bicicletas
        WHERE id = ? AND usuario_id = ?
    """, (bicicleta_id, usuario_id))

    connection.commit()
    connection.close()

    return jsonify({
        "mensagem": "Bicicleta excluída com sucesso!"
    }), 200
