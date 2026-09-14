import sqlite3

connection = sqlite3.connect("database/bikelog.db")

print("Banco de dados BikeLog criado com sucesso!")

connection.close()