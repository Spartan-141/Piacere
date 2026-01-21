import sqlite3
import hashlib
from pathlib import Path

db_path = Path('data/restaurante.db')
if not db_path.exists():
    print(f"Error: {db_path} no existe")
    exit(1)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

admin_pass = "admin"
expected_hash = hashlib.sha256(admin_pass.encode()).hexdigest()

cur.execute("SELECT clave FROM usuarios WHERE usuario='admin'")
row = cur.fetchone()
if row:
    current_hash = row[0]
    print(f"Hash actual en DB: {current_hash}")
    print(f"Hash esperado:     {expected_hash}")
    if current_hash != expected_hash:
        print("Corrigiendo hash del admin...")
        cur.execute("UPDATE usuarios SET clave=? WHERE usuario='admin'", (expected_hash,))
        conn.commit()
        print("Hash corregido exitosamente")
    else:
        print("El hash ya es el correcto (admin)")
else:
    print("Usuario admin no encontrado")

conn.close()
