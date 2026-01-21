# Test script para verificar la migración de contraseñas
import sys
sys.path.insert(0, 'src')

from app.db.connection import crear_conexion
from app.models import Usuario

conn = crear_conexion()
cur = conn.cursor()

# Obtener el usuario admin
cur.execute("SELECT id, usuario, clave FROM usuarios WHERE usuario = 'admin'")
admin = cur.fetchone()

if admin:
    user_id, username, password_hash = admin
    print(f"Usuario: {username}")
    print(f"Hash de contraseña: {password_hash[:50]}...")
    print(f"Es hash bcrypt: {password_hash.startswith('$2')}")
    
    # Probar verificación
    resultado = Usuario.verify_password("admin", password_hash)
    print(f"Verificación de contraseña 'admin': {resultado}")
else:
    print("Usuario admin no encontrado")

conn.close()
