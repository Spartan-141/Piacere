# Test completo del flujo de login
import sys
sys.path.insert(0, 'src')

from app.services.usuarios_service import validar_credenciales

# Probar validación de credenciales
print("Probando validación de credenciales...")
print("Usuario: 'admin', Contraseña: 'admin'")
print()

resultado = validar_credenciales("admin", "admin")

if resultado:
    print("✓ Login exitoso!")
    print(f"  ID: {resultado.id}")
    print(f"  Nombre: {resultado.nombre}")
    print(f"  Usuario: {resultado.usuario}")
    print(f"  Rol: {resultado.rol}")
else:
    print("✗ Login fallido - Credenciales incorrectas")
