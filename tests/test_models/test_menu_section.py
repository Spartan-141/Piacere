"""
Tests para el modelo MenuSection.
"""
import pytest
from app.models.menu_section import MenuSection


class TestMenuSectionCreacion:
    """Tests de creación del modelo MenuSection."""
    
    def test_crear_seccion_completa(self):
        """Debe crear una sección con todos los campos."""
        seccion = MenuSection(
            id=1,
            nombre="Entradas",
            descripcion="Entradas variadas",
            position=1,
            active=True
        )
        
        assert seccion.id == 1
        assert seccion.nombre == "Entradas"
        assert seccion.descripcion == "Entradas variadas"
        assert seccion.position == 1
        assert seccion.active == True
    
    def test_crear_seccion_sin_descripcion(self):
        """Debe crear sección sin descripción."""
        seccion = MenuSection(
            id=1,
            nombre="Bebidas",
            descripcion=None,
            position=2,
            active=True
        )
        
        assert seccion.descripcion is None
    
    def test_crear_seccion_inactiva(self):
        """Debe crear sección inactiva."""
        seccion = MenuSection(
            id=1,
            nombre="Temporal",
            descripcion="Sección temporal",
            position=10,
            active=False
        )
        
        assert seccion.active == False
    
    def test_crear_seccion_sin_id(self):
        """Debe crear sección sin ID (para nuevas secciones)."""
        seccion = MenuSection(
            id=None,
            nombre="Nueva",
            descripcion="Test",
            position=1,
            active=True
        )
        
        assert seccion.id is None


class TestMenuSectionMetodos:
    """Tests de métodos del modelo MenuSection."""
    
    def test_esta_activa_verdadero(self):
        """Debe identificar sección activa."""
        seccion = MenuSection(
            id=1,
            nombre="Activa",
            descripcion=None,
            position=1,
            active=True
        )
        
        assert seccion.esta_activa() == True
    
    def test_esta_activa_falso(self):
        """Debe identificar sección inactiva."""
        seccion = MenuSection(
            id=1,
            nombre="Inactiva",
            descripcion=None,
            position=1,
            active=False
        )
        
        assert seccion.esta_activa() == False
    
    def test_str_representation(self):
        """Debe tener representación string correcta."""
        seccion = MenuSection(
            id=1,
            nombre="Pizzas",
            descripcion="Pizzas artesanales",
            position=1,
            active=True
        )
        
        assert str(seccion) == "Pizzas"


class TestMenuSectionPosition:
    """Tests de posicionamiento de secciones."""
    
    @pytest.mark.parametrize("position", [1, 2, 5, 10, 100])
    def test_posiciones_diversas(self, position):
        """Debe manejar diferentes posiciones."""
        seccion = MenuSection(
            id=1,
            nombre="Test",
            descripcion=None,
            position=position,
            active=True
        )
        
        assert seccion.position == position
    
    def test_position_cero(self):
        """Debe permitir posición cero."""
        seccion = MenuSection(
            id=1,
            nombre="Test",
            descripcion=None,
            position=0,
            active=True
        )
        
        assert seccion.position == 0


class TestMenuSectionFixture:
    """Tests usando fixture."""
    
    def test_usar_fixture_menu_section(self, menu_section_entradas):
        """Debe usar correctamente la fixture de sección."""
        assert menu_section_entradas.nombre == "Entradas"
        assert menu_section_entradas.esta_activa() == True
        assert menu_section_entradas.position == 1


class TestMenuSectionEdgeCases:
    """Tests de casos extremos."""
    
    def test_nombre_vacio(self):
        """Debe manejar nombre vacío."""
        seccion = MenuSection(
            id=1,
            nombre="",
            descripcion=None,
            position=1,
            active=True
        )
        
        assert seccion.nombre == ""
        assert str(seccion) == ""
    
    def test_nombre_muy_largo(self):
        """Debe manejar nombres muy largos."""
        nombre_largo = "A" * 200
        seccion = MenuSection(
            id=1,
            nombre=nombre_largo,
            descripcion=None,
            position=1,
            active=True
        )
        
        assert len(seccion.nombre) == 200
    
    def test_descripcion_muy_larga(self):
        """Debe manejar descripciones muy largas."""
        desc_larga = "X" * 500
        seccion = MenuSection(
            id=1,
            nombre="Test",
            descripcion=desc_larga,
            position=1,
            active=True
        )
        
        assert len(seccion.descripcion) == 500
