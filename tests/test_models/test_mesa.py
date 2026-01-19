"""
Tests para el modelo Mesa.
"""
import pytest
from app.models.mesa import Mesa


class TestMesaCreacion:
    """Tests de creación del modelo Mesa."""
    
    def test_crear_mesa_completa(self):
        """Debe crear una mesa con todos los campos."""
        mesa = Mesa(
            id=1,
            numero=5,
            estado="libre",
            seccion_id=1
        )
        
        assert mesa.id == 1
        assert mesa.numero == 5
        assert mesa.estado == "libre"
        assert mesa.seccion_id == 1
    
    def test_crear_mesa_ocupada(self):
        """Debe crear una mesa ocupada."""
        mesa = Mesa(
            id=2,
            numero=10,
            estado="ocupada",
            seccion_id=1
        )
        
        assert mesa.estado == "ocupada"
    
    def test_crear_mesa_sin_seccion(self):
        """Debe crear una mesa sin sección asignada."""
        mesa = Mesa(
            id=3,
            numero=15,
            estado="libre",
            seccion_id=None
        )
        
        assert mesa.seccion_id is None


class TestMesaMetodos:
    """Tests de métodos del modelo Mesa."""
    
    def test_esta_disponible_libre(self):
        """Mesa libre debe estar disponible."""
        mesa = Mesa(
            id=1,
            numero=5,
            estado="libre",
            seccion_id=1
        )
        
        assert mesa.esta_disponible() == True
    
    def test_esta_disponible_ocupada(self):
        """Mesa ocupada no debe estar disponible."""
        mesa = Mesa(
            id=2,
            numero=10,
            estado="ocupada",
            seccion_id=1
        )
        
        assert mesa.esta_disponible() == False
    
    def test_esta_disponible_reservada(self):
        """Mesa reservada no debe estar disponible."""
        mesa = Mesa(
            id=3,
            numero=15,
            estado="reservada",
            seccion_id=1
        )
        
        assert mesa.esta_disponible() == False


class TestMesaEstados:
    """Tests de diferentes estados de mesa."""
    
    @pytest.mark.parametrize("estado,disponible", [
        ("libre", True),
        ("ocupada", False),
        ("reservada", False),
        ("mantenimiento", False),
    ])
    def test_estados_diversos(self, estado, disponible):
        """Debe manejar diferentes estados correctamente."""
        mesa = Mesa(
            id=1,
            numero=5,
            estado=estado,
            seccion_id=1
        )
        
        assert mesa.esta_disponible() == disponible
        assert mesa.estado == estado


class TestMesaFixtures:
    """Tests usando fixtures."""
    
    def test_fixture_mesa_disponible(self, mesa_disponible):
        """Debe usar correctamente la fixture de mesa disponible."""
        assert mesa_disponible.esta_disponible() == True
        assert mesa_disponible.estado == "libre"
        assert mesa_disponible.numero == 5
    
    def test_fixture_mesa_ocupada(self, mesa_ocupada):
        """Debe usar correctamente la fixture de mesa ocupada."""
        assert mesa_ocupada.esta_disponible() == False
        assert mesa_ocupada.estado == "ocupada"
        assert mesa_ocupada.numero == 10


class TestMesaEdgeCases:
    """Tests de casos extremos."""
    
    def test_numero_mesa_cero(self):
        """Debe manejar número de mesa 0."""
        mesa = Mesa(
            id=1,
            numero=0,
            estado="libre",
            seccion_id=1
        )
        
        assert mesa.numero == 0
    
    def test_numero_mesa_muy_alto(self):
        """Debe manejar números de mesa muy altos."""
        mesa = Mesa(
            id=1,
            numero=9999,
            estado="libre",
            seccion_id=1
        )
        
        assert mesa.numero == 9999
    
    def test_estado_personalizado(self):
        """Debe aceptar estados personalizados."""
        mesa = Mesa(
            id=1,
            numero=5,
            estado="limpieza",
            seccion_id=1
        )
        
        assert mesa.estado == "limpieza"
        assert mesa.esta_disponible() == False  # Solo "libre" está disponible
