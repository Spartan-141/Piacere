"""
Tests para el modelo MenuItem.
"""
import pytest
from datetime import datetime
from app.models.menu_item import MenuItem


class TestMenuItemCreacion:
    """Tests de creación del modelo MenuItem."""
    
    def test_crear_item_completo(self):
        """Debe crear un item con todos los campos."""
        now = datetime.now()
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Pizza Margarita",
            descripcion="Pizza clásica",
            precio=15.50,
            disponible=True,
            position=1,
            created_at=now
        )
        
        assert item.id == 1
        assert item.section_id == 1
        assert item.nombre == "Pizza Margarita"
        assert item.descripcion == "Pizza clásica"
        assert item.precio == 15.50
        assert item.disponible == True
        assert item.position == 1
        assert item.created_at == now
    
    def test_crear_item_sin_descripcion(self):
        """Debe crear item sin descripción."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Item",
            descripcion=None,
            precio=10.0,
            disponible=True,
            position=1
        )
        
        assert item.descripcion is None
    
    def test_crear_item_sin_created_at(self):
        """Debe crear item sin fecha de creación."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Item",
            descripcion="Test",
            precio=10.0,
            disponible=True,
            position=1
        )
        
        assert item.created_at is None
    
    def test_crear_item_no_disponible(self):
        """Debe crear item no disponible."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Item",
            descripcion=None,
            precio=10.0,
            disponible=False,
            position=1
        )
        
        assert item.disponible == False


class TestMenuItemMetodos:
    """Tests de métodos del modelo MenuItem."""
    
    def test_esta_disponible_verdadero(self):
        """Debe identificar item disponible."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Test",
            descripcion=None,
            precio=10.0,
            disponible=True,
            position=1
        )
        
        assert item.esta_disponible() == True
    
    def test_esta_disponible_falso(self):
        """Debe identificar item no disponible."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Test",
            descripcion=None,
            precio=10.0,
            disponible=False,
            position=1
        )
        
        assert item.esta_disponible() == False
    
    def test_marcar_no_disponible(self):
        """Debe marcar item como no disponible."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Test",
            descripcion=None,
            precio=10.0,
            disponible=True,
            position=1
        )
        
        item.marcar_no_disponible()
        
        assert item.disponible == False
        assert item.esta_disponible() == False
    
    def test_marcar_disponible(self):
        """Debe marcar item como disponible."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Test",
            descripcion=None,
            precio=10.0,
            disponible=False,
            position=1
        )
        
        item.marcar_disponible()
        
        assert item.disponible == True
        assert item.esta_disponible() == True
    
    def test_alternar_disponibilidad(self):
        """Debe poder alternar disponibilidad múltiples veces."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Test",
            descripcion=None,
            precio=10.0,
            disponible=True,
            position=1
        )
        
        item.marcar_no_disponible()
        assert item.disponible == False
        
        item.marcar_disponible()
        assert item.disponible == True
        
        item.marcar_no_disponible()
        assert item.disponible == False
    
    def test_get_precio_formateado(self):
        """Debe formatear precio correctamente."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Test",
            descripcion=None,
            precio=12.50,
            disponible=True,
            position=1
        )
        
        assert item.get_precio_formateado() == "$12.50"
    
    def test_str_representation(self):
        """Debe tener representación string correcta."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Pizza Napolitana",
            descripcion="Deliciosa",
            precio=18.0,
            disponible=True,
            position=1
        )
        
        assert str(item) == "Pizza Napolitana"


class TestMenuItemFixture:
    """Tests usando fixture."""
    
    def test_usar_fixture_menu_item(self, menu_item_ensalada):
        """Debe usar correctamente la fixture de item."""
        assert menu_item_ensalada.nombre == "Ensalada César"
        assert menu_item_ensalada.precio == 12.50
        assert menu_item_ensalada.esta_disponible() == True


class TestMenuItemEdgeCases:
    """Tests de casos extremos."""
    
    def test_precio_cero(self):
        """Debe permitir precio cero."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Gratis",
            descripcion=None,
            precio=0.0,
            disponible=True,
            position=1
        )
        
        assert item.precio == 0.0
        assert item.get_precio_formateado() == "$0.00"
    
    def test_precio_muy_alto(self):
        """Debe manejar precios muy altos."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Premium",
            descripcion=None,
            precio=999999.99,
            disponible=True,
            position=1
        )
        
        assert item.precio == 999999.99
    
    def test_position_negativa(self):
        """Debe permitir posición negativa (para ordenamiento especial)."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="Test",
            descripcion=None,
            precio=10.0,
            disponible=True,
            position=-1
        )
        
        assert item.position == -1
    
    def test_nombre_vacio(self):
        """Debe manejar nombre vacío."""
        item = MenuItem(
            id=1,
            section_id=1,
            nombre="",
            descripcion=None,
            precio=10.0,
            disponible=True,
            position=1
        )
        
        assert item.nombre == ""
        assert str(item) == ""
