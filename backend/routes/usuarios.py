from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios", methods=["POST"])
def cadastrar_usuario():
    dados = request.get_json()

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    if not nome or not email or not senha:
        return jsonify({
            "erro": "Nome, email e senha são obrigatórios."
        }), 400

    senha_hash = generate_password_hash(senha)

    connection = get_db_connection()

    usuario_existente = connection.execute("""
        SELECT id
        FROM usuarios
        WHERE email = ?
    """, (email,)).fetchone()

    if usuario_existente:
        connection.close()
        return jsonify({
            "erro": "Já existe um usuário com esse email."
        }), 409

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha)
        VALUES (?, ?, ?)
    """, (
        nome,
        email,
        senha_hash
    ))

    connection.commit()

    usuario_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "mensagem": "Usuário cadastrado com sucesso!",
        "usuario": {
            "id": usuario_id,
            "nome": nome,
            "email": email
        }
    }), 201

@usuarios_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()

    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({
            "erro": "Email e senha são obrigatórios."
        }), 400

    connection = get_db_connection()

    usuario = connection.execute("""
        SELECT id, nome, email, senha
        FROM usuarios
        WHERE email = ?
    """, (email,)).fetchone()

    connection.close()

    if usuario is None or not check_password_hash(usuario["senha"], senha):
        return jsonify({
            "erro": "Email ou senha inválidos."
        }), 401

    session.clear()
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]

    return jsonify({
        "mensagem": "Login realizado com sucesso!",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"]
        }
    }), 200


@usuarios_bp.route("/me", methods=["GET"])
def usuario_logado():
    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    return jsonify({
        "id": usuario_id,
        "nome": session.get("usuario_nome")
    }), 200


@usuarios_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "mensagem": "Logout realizado com sucesso!"
    }), 200