import sqlite3

connection = sqlite3.connect("database/bikelog.db")
cursor = connection.cursor()

# Cadastrar usuário somente se o e-mail ainda não existir
cursor.execute("""
SELECT id
FROM usuarios
WHERE email = ?
""", ("willian@email.com",))

usuario = cursor.fetchone()

if usuario is None:
    cursor.execute("""
    INSERT INTO usuarios (nome, email, senha)
    VALUES (?, ?, ?)
    """, ("Willian", "willian@email.com", "123456"))

    connection.commit()

    usuario_id = cursor.lastrowid

    print("\nUsuário cadastrado com sucesso!")
else:
    usuario_id = usuario[0]

    print("\nUsuário já estava cadastrado.")

# Consultar usuários
cursor.execute("""
SELECT id, nome, email, created_at
FROM usuarios
""")

usuarios = cursor.fetchall()

print("\n--- USUÁRIOS ---")

for usuario in usuarios:
    print(usuario)

# Verificar se a bicicleta já existe
cursor.execute("""
SELECT id
FROM bicicletas
WHERE usuario_id = ? AND nome = ?
""", (usuario_id, "Minha Speed"))

bicicleta = cursor.fetchone()

if bicicleta is None:
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
        "Minha Speed",
        "Caloi",
        "Strada",
        "Speed"
    ))

    connection.commit()

    bicicleta_id = cursor.lastrowid

    print("\nBicicleta cadastrada com sucesso!")
else:
    bicicleta_id = bicicleta[0]

    print("\nBicicleta já estava cadastrada.")

cursor.execute("""
SELECT
    bicicletas.id,
    bicicletas.nome,
    bicicletas.marca,
    bicicletas.modelo,
    bicicletas.tipo,
    usuarios.nome
FROM bicicletas
JOIN usuarios
    ON bicicletas.usuario_id = usuarios.id
""")

bicicletas = cursor.fetchall()

print("\n--- BICICLETAS ---")

for bicicleta in bicicletas:
    print(bicicleta)

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
    "2026-09-14",
    45.0,
    90,
    30.0,
    "Pedal de teste do BikeLog"
))

connection.commit()

print("\nPedalada cadastrada com sucesso!")

cursor.execute("""
SELECT
    pedaladas.id,
    usuarios.nome,
    bicicletas.nome,
    pedaladas.data,
    pedaladas.distancia_km,
    pedaladas.duracao_minutos,
    pedaladas.velocidade_media,
    pedaladas.observacoes
FROM pedaladas
JOIN usuarios
    ON pedaladas.usuario_id = usuarios.id
JOIN bicicletas
    ON pedaladas.bicicleta_id = bicicletas.id
""")

pedaladas = cursor.fetchall()

print("\n--- PEDALADAS ---")

for pedalada in pedaladas:
    print(pedalada)

connection.close()