import sqlite3

connection = sqlite3.connect("database/bikelog.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bicicletas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    marca TEXT,
    modelo TEXT,
    tipo TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pedaladas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    bicicleta_id INTEGER NOT NULL,
    data DATE NOT NULL,
    distancia_km REAL NOT NULL,
    duracao_minutos INTEGER NOT NULL,
    velocidade_media REAL NOT NULL,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id),

    FOREIGN KEY (bicicleta_id)
        REFERENCES bicicletas(id)
)
""")

connection.commit()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
""")

tabelas = cursor.fetchall()

print(tabelas)
print("Banco de dados criado com sucesso!")

connection.close()