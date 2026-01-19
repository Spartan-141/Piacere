"""
Tests para el modelo Factura.
"""
import pytest
from datetime import datetime
from app.models.factura import Factura


class TestFacturaCreacion:
    """Tests de creación del modelo Factura."""
    
    def test_crear_factura_completa(self):
        """Debe crear una factura con todos los campos."""
        now = datetime.now()
        factura = Factura(
            id=1,
            orden_id=5,
            numero_factura="20240115-001",
            fecha=now,
            cliente_nombre="Juan Pérez",
            total=125.50
        )
        
        assert factura.id == 1
        assert factura.orden_id == 5
        assert factura.numero_factura == "20240115-001"
        assert factura.fecha == now
        assert factura.cliente_nombre == "Juan Pérez"
        assert factura.total == 125.50
    
    def test_crear_factura_sin_id(self):
        """Debe crear factura sin ID (para nuevas facturas)."""
        factura = Factura(
            id=None,
            orden_id=1,
            numero_factura="TEST-001",
            fecha=datetime.now(),
            cliente_nombre="Test",
            total=0.0
        )
        
        assert factura.id is None


class TestFacturaFormato:
    """Tests de métodos de formateo."""
    
    def test_get_numero_formateado(self):
        """Debe formatear número de factura correctamente."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="20240115-001",
            fecha=datetime.now(),
            cliente_nombre="Test",
            total=100.0
        )
        
        assert factura.get_numero_formateado() == "FAC-20240115-001"
    
    def test_get_total_formateado(self):
        """Debe formatear total correctamente."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha=datetime.now(),
            cliente_nombre="Test",
            total=125.50
        )
        
        assert factura.get_total_formateado() == "$125.50"
    
    def test_get_fecha_formateada_default(self):
        """Debe formatear fecha con formato por defecto."""
        fecha = datetime(2024, 1, 15, 14, 30, 0)
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha=fecha,
            cliente_nombre="Test",
            total=100.0
        )
        
        assert factura.get_fecha_formateada() == "15/01/2024 14:30"
    
    def test_get_fecha_formateada_custom(self):
        """Debe formatear fecha con formato personalizado."""
        fecha = datetime(2024, 1, 15, 14, 30, 0)
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha=fecha,
            cliente_nombre="Test",
            total=100.0
        )
        
        assert factura.get_fecha_formateada("%Y-%m-%d") == "2024-01-15"
    
    def test_get_fecha_formateada_desde_string(self):
        """Debe manejar fecha como string (de BD)."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha="2024-01-15 14:30:00",
            cliente_nombre="Test",
            total=100.0
        )
        
        resultado = factura.get_fecha_formateada()
        assert "15/01/2024" in resultado
    
    def test_str_representation(self):
        """Debe tener representación string correcta."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="20240115-001",
            fecha=datetime.now(),
            cliente_nombre="María García",
            total=150.75
        )
        
        assert str(factura) == "FAC-20240115-001 - María García - $150.75"


class TestFacturaFixture:
    """Tests usando fixture."""
    
    def test_usar_fixture_factura(self, factura_ejemplo):
        """Debe usar correctamente la fixture de factura."""
        assert factura_ejemplo.numero_factura == "FACT-20240115-001"
        assert factura_ejemplo.cliente_nombre == "María García"
        assert factura_ejemplo.total == 125.50


class TestFacturaEdgeCases:
    """Tests de casos extremos."""
    
    def test_total_cero(self):
        """Debe manejar total cero."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha=datetime.now(),
            cliente_nombre="Test",
            total=0.0
        )
        
        assert factura.total == 0.0
        assert factura.get_total_formateado() == "$0.00"
    
    def test_total_muy_alto(self):
        """Debe manejar totales muy altos."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha=datetime.now(),
            cliente_nombre="Test",
            total=999999.99
        )
        
        assert factura.total == 999999.99
    
    def test_numero_factura_vacio(self):
        """Debe manejar número de factura vacío."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="",
            fecha=datetime.now(),
            cliente_nombre="Test",
            total=100.0
        )
        
        assert factura.numero_factura == ""
        assert factura.get_numero_formateado() == "FAC-"
    
    def test_cliente_nombre_vacio(self):
        """Debe manejar nombre de cliente vacío."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha=datetime.now(),
            cliente_nombre="",
            total=100.0
        )
        
        assert factura.cliente_nombre == ""
    
    def test_fecha_string_invalido(self):
        """Debe manejar fecha string inválido."""
        factura = Factura(
            id=1,
            orden_id=1,
            numero_factura="001",
            fecha="fecha_invalida",
            cliente_nombre="Test",
            total=100.0
        )
        
        # Debe retornar el string original si no puede parsear
        resultado = factura.get_fecha_formateada()
        assert resultado == "fecha_invalida"
