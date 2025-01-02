import sqlite3
db_path = "path_to/signaturits_metadata.db"
connection = sqlite3.connect(db_path)

connection.close()