"""
Tests para el modelo Seccion.
"""
import pytest
from app.models.seccion import Seccion


class TestSeccionCreacion:
    """Tests de creación del modelo Seccion."""
    
    def test_crear_seccion_completa(self):
        """Debe crear una sección con todos los campos."""
        seccion = Seccion(id=1, nombre="Salón Principal")
        
        assert seccion.id == 1
        assert seccion.nombre == "Salón Principal"
    
    def test_crear_seccion_sin_id(self):
        """Debe crear sección sin ID (para nuevas secciones)."""
        seccion = Seccion(id=None, nombre="Nueva Sección")
        
        assert seccion.id is None
        assert seccion.nombre == "Nueva Sección"
    
    def test_str_representation(self):
        """Debe tener representación string correcta."""
        seccion = Seccion(id=1, nombre="Terraza")
        
        assert str(seccion) == "Terraza"


class TestSeccionFixture:
    """Tests usando fixture."""
    
    def test_usar_fixture_seccion(self, seccion_principal):
        """Debe usar correctamente la fixture de sección."""
        assert seccion_principal.nombre == "Salón Principal"
        assert seccion_principal.id == 1


class TestSeccionEdgeCases:
    """Tests de casos extremos."""
    
    def test_nombre_vacio(self):
        """Debe manejar nombre vacío."""
        seccion = Seccion(id=1, nombre="")
        
        assert seccion.nombre == ""
        assert str(seccion) == ""
    
    def test_nombre_muy_largo(self):
        """Debe manejar nombres muy largos."""
        nombre_largo = "A" * 500
        seccion = Seccion(id=1, nombre=nombre_largo)
        
        assert len(seccion.nombre) == 500
    
    def test_nombre_con_caracteres_especiales(self):
        """Debe manejar nombres con caracteres especiales."""
        seccion = Seccion(id=1, nombre="Sección #1 (VIP) - Área Especial")
        
        assert seccion.nombre == "Sección #1 (VIP) - Área Especial"
