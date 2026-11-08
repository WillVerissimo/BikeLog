from contextlib import closing
from datetime import date
from math import isfinite
from flask import Blueprint, request, jsonify, session
from database import get_db_connection

pedaladas_bp = Blueprint("pedaladas", __name__)

def validar(dados):
    if not isinstance(dados, dict):
        return None, "Envie um JSON válido."
    try:
        if isinstance(dados.get("bicicleta_id"), bool) or isinstance(dados.get("duracao_minutos"), bool):
            raise ValueError()
        bicicleta_id = int(dados.get("bicicleta_id"))
        data = date.fromisoformat(dados.get("data", ""))
        distancia = float(dados.get("distancia_km"))
        duracao_valor = float(dados.get("duracao_minutos"))
        if not isfinite(duracao_valor) or not duracao_valor.is_integer():
            raise ValueError()
        duracao = int(duracao_valor)
        if bicicleta_id <= 0 or not isfinite(distancia) or distancia <= 0 or duracao <= 0:
            raise ValueError()
    except (ValueError, TypeError, OverflowError):
        return None, "Informe bicicleta, data (AAAA-MM-DD), distância e duração válidas e positivas."
    observacoes = dados.get("observacoes") or ""
    if not isinstance(observacoes, str) or len(observacoes) > 1000:
        return None, "Observações devem ter até 1000 caracteres."
    return (bicicleta_id, data.isoformat(), distancia, duracao, round(distancia / (duracao / 60), 2), observacoes), None

def autenticado():
    return session.get("usuario_id")

@pedaladas_bp.route("/pedaladas", methods=["POST"])
def cadastrar_pedalada():
    usuario_id = autenticado()
    if usuario_id is None:
        return jsonify(erro="Usuário não autenticado."), 401
    valores, erro = validar(request.get_json(silent=True))
    if erro:
        return jsonify(erro=erro), 400
    with closing(get_db_connection()) as db, db:
        bicicleta = db.execute("SELECT id FROM bicicletas WHERE id=? AND usuario_id=?", (valores[0], usuario_id)).fetchone()
        if not bicicleta:
            return jsonify(erro="Bicicleta não encontrada."), 404
        cursor = db.execute("""INSERT INTO pedaladas (usuario_id, bicicleta_id, data, distancia_km, duracao_minutos, velocidade_media, observacoes)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""", (usuario_id, *valores))
        pedalada_id = cursor.lastrowid
    return jsonify(mensagem="Pedalada cadastrada!", id=pedalada_id), 201

@pedaladas_bp.route("/pedaladas", methods=["GET"])
def listar_pedaladas():
    usuario_id = autenticado()
    if usuario_id is None:
        return jsonify(erro="Usuário não autenticado."), 401
    with closing(get_db_connection()) as db:
        rows = db.execute("""SELECT p.id, p.bicicleta_id, b.nome AS bicicleta_nome, p.data,
                                p.distancia_km, p.duracao_minutos, p.velocidade_media, p.observacoes
                         FROM pedaladas p JOIN bicicletas b ON b.id=p.bicicleta_id
                         WHERE p.usuario_id=? ORDER BY p.data DESC, p.id DESC""", (usuario_id,)).fetchall()
    return jsonify([dict(row) for row in rows]), 200

@pedaladas_bp.route("/pedaladas/<int:pedalada_id>", methods=["PUT"])
def editar_pedalada(pedalada_id):
    usuario_id = autenticado()
    if usuario_id is None:
        return jsonify(erro="Usuário não autenticado."), 401
    valores, erro = validar(request.get_json(silent=True))
    if erro:
        return jsonify(erro=erro), 400
    with closing(get_db_connection()) as db, db:
        existente = db.execute("SELECT id FROM pedaladas WHERE id=? AND usuario_id=?", (pedalada_id, usuario_id)).fetchone()
        if not existente:
            return jsonify(erro="Pedalada não encontrada."), 404
        bicicleta = db.execute("SELECT id FROM bicicletas WHERE id=? AND usuario_id=?", (valores[0], usuario_id)).fetchone()
        if not bicicleta:
            return jsonify(erro="Bicicleta não encontrada."), 404
        db.execute("""UPDATE pedaladas SET bicicleta_id=?, data=?, distancia_km=?, duracao_minutos=?,
                      velocidade_media=?, observacoes=? WHERE id=? AND usuario_id=?""", (*valores, pedalada_id, usuario_id))
    return jsonify(mensagem="Pedalada atualizada!"), 200

@pedaladas_bp.route("/pedaladas/<int:pedalada_id>", methods=["DELETE"])
def excluir_pedalada(pedalada_id):
    usuario_id = autenticado()
    if usuario_id is None:
        return jsonify(erro="Usuário não autenticado."), 401
    with closing(get_db_connection()) as db, db:
        cursor = db.execute("DELETE FROM pedaladas WHERE id=? AND usuario_id=?", (pedalada_id, usuario_id))
        if cursor.rowcount == 0:
            return jsonify(erro="Pedalada não encontrada."), 404
    return jsonify(mensagem="Pedalada excluída!"), 200
