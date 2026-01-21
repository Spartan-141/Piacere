# Test para verificar el problema del login
import sys
import hashlib
sys.path.insert(0, 'src')

from app.db.connection import crear_conexion
from app.models import Usuario

# Obtener el hash almacenado
conn = crear_conexion()
cur = conn.cursor()
cur.execute("SELECT clave FROM usuarios WHERE usuario = 'admin'")
stored_hash = cur.fetchone()[0]
conn.close()

# Generar hash de "admin"
test_password = "admin"
generated_hash = hashlib.sha256(test_password.encode()).hexdigest()

print(f"Hash almacenado: {stored_hash}")
print(f"Hash generado:   {generated_hash}")
print(f"¿Coinciden?: {stored_hash == generated_hash}")
print()
print(f"Verificación con Usuario.verify_password: {Usuario.verify_password(test_password, stored_hash)}")
