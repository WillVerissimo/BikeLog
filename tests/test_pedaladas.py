"""Testes de integração da AC3. Execute: python -m unittest discover -s tests -v"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from flask import Flask
from routes.pedaladas import pedaladas_bp

class TestPedaladas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "teste.db")
        db = sqlite3.connect(self.path)
        db.executescript("""
            CREATE TABLE bicicletas (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL, nome TEXT);
            CREATE TABLE pedaladas (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL,
                bicicleta_id INTEGER NOT NULL, data TEXT, distancia_km REAL,
                duracao_minutos INTEGER, velocidade_media REAL, observacoes TEXT);
            INSERT INTO bicicletas VALUES (1,1,'Speed'),(2,2,'MTB');
        """)
        db.commit()
        db.close()
        def conectar():
            conn = sqlite3.connect(self.path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        self.patch = patch("routes.pedaladas.get_db_connection", side_effect=conectar)
        self.patch.start()
        app = Flask(__name__)
        app.secret_key = "chave-de-testes"
        app.register_blueprint(pedaladas_bp)
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def login(self, usuario):
        with self.client.session_transaction() as sess:
            sess["usuario_id"] = usuario

    def dados(self, bicicleta=1):
        return {"bicicleta_id": bicicleta, "data": "2026-11-08",
                "distancia_km": 40.0, "duracao_minutos": 120,
                "observacoes": "Treino"}

    def test_exige_login(self):
        self.assertEqual(self.client.get("/pedaladas").status_code, 401)
        self.assertEqual(self.client.post("/pedaladas", json=self.dados()).status_code, 401)

    def test_crud_e_estatisticas(self):
        self.login(1)
        r = self.client.post("/pedaladas", json=self.dados())
        self.assertEqual(r.status_code, 201)
        pid = r.json["id"]
        lista = self.client.get("/pedaladas").json
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0]["velocidade_media"], 20.0)
        novo = self.dados()
        novo["distancia_km"] = 60
        self.assertEqual(self.client.put(f"/pedaladas/{pid}", json=novo).status_code, 200)
        self.assertEqual(self.client.get("/pedaladas").json[0]["velocidade_media"], 30.0)
        self.assertEqual(self.client.delete(f"/pedaladas/{pid}").status_code, 200)
        self.assertEqual(self.client.get("/pedaladas").json, [])

    def test_nao_acessa_outro_usuario(self):
        self.login(1)
        self.assertEqual(self.client.post("/pedaladas", json=self.dados(2)).status_code, 404)
        pid = self.client.post("/pedaladas", json=self.dados()).json["id"]
        self.login(2)
        self.assertEqual(self.client.get("/pedaladas").json, [])
        self.assertEqual(self.client.put(f"/pedaladas/{pid}", json=self.dados(2)).status_code, 404)
        self.assertEqual(self.client.delete(f"/pedaladas/{pid}").status_code, 404)

    def test_valida_entradas(self):
        self.login(1)
        for alteracao in ({"distancia_km": -1}, {"duracao_minutos": 0},
                          {"duracao_minutos": 1.5}, {"data": "2026-99-99"},
                          {"distancia_km": "NaN"}):
            with self.subTest(alteracao=alteracao):
                dados = {**self.dados(), **alteracao}
                self.assertEqual(self.client.post("/pedaladas", json=dados).status_code, 400)

if __name__ == "__main__":
    unittest.main()
