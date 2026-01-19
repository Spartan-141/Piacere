"""
Tests para el modelo Usuario.
"""
import pytest
from app.models.usuario import Usuario


class TestUsuarioCreacion:
    """Tests de creación del modelo Usuario."""
    
    def test_crear_usuario_completo(self):
        """Debe crear un usuario con todos los campos."""
        usuario = Usuario(
            id=1,
            nombre="Juan",
            apellido="Pérez",
            usuario="jperez",
            clave="password123",
            rol="mesero"
        )
        
        assert usuario.id == 1
        assert usuario.nombre == "Juan"
        assert usuario.apellido == "Pérez"
        assert usuario.usuario == "jperez"
        assert usuario.clave == "password123"
        assert usuario.rol == "mesero"
    
    def test_crear_usuario_admin(self):
        """Debe crear un usuario administrador."""
        usuario = Usuario(
            id=1,
            nombre="Admin",
            apellido=None,
            usuario="admin",
            clave="admin123",
            rol="admin"
        )
        
        assert usuario.rol == "admin"
        assert usuario.apellido is None
    
    def test_crear_usuario_sin_apellido(self):
        """Debe crear un usuario sin apellido."""
        usuario = Usuario(
            id=1,
            nombre="Test",
            apellido=None,
            usuario="test",
            clave="test123",
            rol="mesero"
        )
        
        assert usuario.apellido is None


class TestUsuarioMetodos:
    """Tests de métodos del modelo Usuario."""
    
    def test_es_admin_verdadero(self):
        """Debe identificar correctamente un administrador."""
        usuario = Usuario(
            id=1,
            nombre="Admin",
            apellido=None,
            usuario="admin",
            clave="admin123",
            rol="admin"
        )
        
        assert usuario.es_admin() == True
    
    def test_es_admin_falso_mesero(self):
        """Debe identificar que un mesero no es admin."""
        usuario = Usuario(
            id=1,
            nombre="Mesero",
            apellido=None,
            usuario="mesero",
            clave="mesero123",
            rol="mesero"
        )
        
        assert usuario.es_admin() == False
    
    def test_puede_gestionar_usuarios(self):
        """Solo admin puede gestionar usuarios."""
        admin = Usuario(id=1, nombre="Admin", apellido=None, usuario="admin", clave="123", rol="admin")
        mesero = Usuario(id=2, nombre="Mesero", apellido=None, usuario="mesero", clave="123", rol="mesero")
        
        assert admin.puede_gestionar_usuarios() == True
        assert mesero.puede_gestionar_usuarios() == False
    
    def test_puede_tomar_ordenes(self):
        """Mesero y admin pueden tomar órdenes."""
        admin = Usuario(id=1, nombre="Admin", apellido=None, usuario="admin", clave="123", rol="admin")
        mesero = Usuario(id=2, nombre="Mesero", apellido=None, usuario="mesero", clave="123", rol="mesero")
        cajero = Usuario(id=3, nombre="Cajero", apellido=None, usuario="cajero", clave="123", rol="cajero")
        
        assert admin.puede_tomar_ordenes() == True
        assert mesero.puede_tomar_ordenes() == True
        assert cajero.puede_tomar_ordenes() == False
    
    def test_puede_facturar(self):
        """Cajero y admin pueden facturar."""
        admin = Usuario(id=1, nombre="Admin", apellido=None, usuario="admin", clave="123", rol="admin")
        cajero = Usuario(id=2, nombre="Cajero", apellido=None, usuario="cajero", clave="123", rol="cajero")
        mesero = Usuario(id=3, nombre="Mesero", apellido=None, usuario="mesero", clave="123", rol="mesero")
        
        assert admin.puede_facturar() == True
        assert cajero.puede_facturar() == True
        assert mesero.puede_facturar() == False
    
    def test_puede_gestionar_inventario(self):
        """Solo admin puede gestionar inventario."""
        admin = Usuario(id=1, nombre="Admin", apellido=None, usuario="admin", clave="123", rol="admin")
        mesero = Usuario(id=2, nombre="Mesero", apellido=None, usuario="mesero", clave="123", rol="mesero")
        
        assert admin.puede_gestionar_inventario() == True
        assert mesero.puede_gestionar_inventario() == False
    
    def test_get_nombre_completo_con_apellido(self):
        """Debe retornar nombre completo con apellido."""
        usuario = Usuario(
            id=1,
            nombre="Juan",
            apellido="Pérez",
            usuario="jperez",
            clave="123",
            rol="mesero"
        )
        
        assert usuario.get_nombre_completo() == "Juan Pérez"
    
    def test_get_nombre_completo_sin_apellido(self):
        """Debe retornar solo nombre si no hay apellido."""
        usuario = Usuario(
            id=1,
            nombre="Juan",
            apellido=None,
            usuario="jperez",
            clave="123",
            rol="mesero"
        )
        
        assert usuario.get_nombre_completo() == "Juan"


class TestUsuarioRoles:
    """Tests de diferentes roles de usuario."""
    
    @pytest.mark.parametrize("rol,es_admin,puede_ordenes,puede_fact", [
        ("admin", True, True, True),
        ("mesero", False, True, False),
        ("cajero", False, False, True),
        ("cocinero", False, False, False),
    ])
    def test_roles_diversos(self, rol, es_admin, puede_ordenes, puede_fact):
        """Debe manejar diferentes roles correctamente."""
        usuario = Usuario(
            id=1,
            nombre="Test",
            apellido=None,
            usuario="test",
            clave="123",
            rol=rol
        )
        
        assert usuario.es_admin() == es_admin
        assert usuario.puede_tomar_ordenes() == puede_ordenes
        assert usuario.puede_facturar() == puede_fact


class TestUsuarioFixtures:
    """Tests usando fixtures."""
    
    def test_fixture_usuario_admin(self, usuario_admin):
        """Debe usar correctamente la fixture de admin."""
        assert usuario_admin.es_admin() == True
        assert usuario_admin.rol == "admin"
        assert usuario_admin.puede_gestionar_usuarios() == True
    
    def test_fixture_usuario_mesero(self, usuario_mesero):
        """Debe usar correctamente la fixture de mesero."""
        assert usuario_mesero.es_admin() == False
        assert usuario_mesero.rol == "mesero"
        assert usuario_mesero.puede_tomar_ordenes() == True


class TestUsuarioSeguridad:
    """Tests de funciones de seguridad."""
    
    def test_hash_password(self):
        """Debe hashear contraseñas correctamente."""
        password = "mi_password_seguro"
        hashed = Usuario.hash_password(password)
        
        assert hashed != password
        assert len(hashed) == 64  # SHA256 produce 64 caracteres hex
    
    def test_hash_password_consistente(self):
        """El mismo password debe producir el mismo hash."""
        password = "test123"
        hash1 = Usuario.hash_password(password)
        hash2 = Usuario.hash_password(password)
        
        assert hash1 == hash2


class TestUsuarioEdgeCases:
    """Tests de casos extremos."""
    
    def test_nombre_vacio(self):
        """Debe manejar nombre vacío."""
        usuario = Usuario(
            id=1,
            nombre="",
            apellido=None,
            usuario="test",
            clave="123",
            rol="mesero"
        )
        
        assert usuario.nombre == ""
        assert usuario.get_nombre_completo() == ""
    
    def test_nombre_muy_largo(self):
        """Debe manejar nombres muy largos."""
        nombre_largo = "A" * 200
        usuario = Usuario(
            id=1,
            nombre=nombre_largo,
            apellido=None,
            usuario="test",
            clave="123",
            rol="mesero"
        )
        
        assert len(usuario.nombre) == 200
    
    def test_rol_personalizado(self):
        """Debe aceptar roles personalizados."""
        usuario = Usuario(
            id=1,
            nombre="Test",
            apellido=None,
            usuario="test",
            clave="123",
            rol="supervisor"
        )
        
        assert usuario.rol == "supervisor"
        assert usuario.es_admin() == False  # Solo "admin" es admin
