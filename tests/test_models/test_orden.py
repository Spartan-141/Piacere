"""
Tests para el modelo Orden.
"""
import pytest
from datetime import datetime
from app.models.orden import Orden


class TestOrdenCreacion:
    """Tests de creación del modelo Orden."""
    
    def test_crear_orden_completa(self):
        """Debe crear una orden con todos los campos."""
        now = datetime.now()
        orden = Orden(
            id=1,
            mesa_id=5,
            cliente_nombre="Juan Pérez",
            estado="abierta",
            total=125.50,
            fecha=now,
            actualizado_en=None,
            cerrado_en=None
        )
        
        assert orden.id == 1
        assert orden.mesa_id == 5
        assert orden.cliente_nombre == "Juan Pérez"
        assert orden.estado == "abierta"
        assert orden.total == 125.50
        assert orden.fecha == now
        assert orden.actualizado_en is None
        assert orden.cerrado_en is None
    
    def test_crear_orden_sin_id(self):
        """Debe crear orden sin ID (para nuevas órdenes)."""
        orden = Orden(
            id=None,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=0.0,
            fecha=datetime.now()
        )
        
        assert orden.id is None


class TestOrdenEstado:
    """Tests de gestión de estado de orden."""
    
    def test_esta_abierta_verdadero(self):
        """Debe identificar orden abierta."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=0.0,
            fecha=datetime.now()
        )
        
        assert orden.esta_abierta() == True
        assert orden.esta_cerrada() == False
    
    def test_esta_cerrada_verdadero(self):
        """Debe identificar orden cerrada."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="cerrada",
            total=100.0,
            fecha=datetime.now()
        )
        
        assert orden.esta_cerrada() == True
        assert orden.esta_abierta() == False
    
    def test_cerrar_orden(self):
        """Debe cerrar orden correctamente."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=50.0,
            fecha=datetime.now()
        )
        
        orden.cerrar()
        
        assert orden.estado == "cerrada"
        assert orden.cerrado_en is not None
        assert isinstance(orden.cerrado_en, datetime)
    
    def test_abrir_orden(self):
        """Debe abrir orden correctamente."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="cerrada",
            total=50.0,
            fecha=datetime.now(),
            cerrado_en=datetime.now()
        )
        
        orden.abrir()
        
        assert orden.estado == "abierta"
        assert orden.cerrado_en is None
    
    def test_alternar_estado_multiples_veces(self):
        """Debe poder alternar estado múltiples veces."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=0.0,
            fecha=datetime.now()
        )
        
        orden.cerrar()
        assert orden.esta_cerrada() == True
        
        orden.abrir()
        assert orden.esta_abierta() == True
        
        orden.cerrar()
        assert orden.esta_cerrada() == True


class TestOrdenTotal:
    """Tests de gestión del total de la orden."""
    
    def test_actualizar_total(self):
        """Debe actualizar total correctamente."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=0.0,
            fecha=datetime.now()
        )
        
        orden.actualizar_total(125.50)
        
        assert orden.total == 125.50
        assert orden.actualizado_en is not None
        assert isinstance(orden.actualizado_en, datetime)
    
    def test_actualizar_total_multiples_veces(self):
        """Debe poder actualizar total múltiples veces."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=0.0,
            fecha=datetime.now()
        )
        
        orden.actualizar_total(50.0)
        assert orden.total == 50.0
        
        orden.actualizar_total(75.25)
        assert orden.total == 75.25
        
        orden.actualizar_total(100.0)
        assert orden.total == 100.0
    
    def test_get_total_formateado(self):
        """Debe formatear total correctamente."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=125.50,
            fecha=datetime.now()
        )
        
        assert orden.get_total_formateado() == "$125.50"


class TestOrdenRepresentacion:
    """Tests de representación de orden."""
    
    def test_str_representation(self):
        """Debe tener representación string correcta."""
        orden = Orden(
            id=15,
            mesa_id=5,
            cliente_nombre="María García",
            estado="abierta",
            total=75.0,
            fecha=datetime.now()
        )
        
        assert str(orden) == "Orden #15 - Mesa 5 - María García"


class TestOrdenFixture:
    """Tests usando fixture."""
    
    def test_usar_fixture_orden(self, orden_abierta):
        """Debe usar correctamente la fixture de orden."""
        assert orden_abierta.cliente_nombre == "Juan Pérez"
        assert orden_abierta.esta_abierta() == True
        assert orden_abierta.mesa_id == 1


class TestOrdenEdgeCases:
    """Tests de casos extremos."""
    
    def test_total_cero(self):
        """Debe manejar total cero."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=0.0,
            fecha=datetime.now()
        )
        
        assert orden.total == 0.0
        assert orden.get_total_formateado() == "$0.00"
    
    def test_total_negativo(self):
        """Debe manejar total negativo (para devoluciones)."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="Test",
            estado="abierta",
            total=-50.0,
            fecha=datetime.now()
        )
        
        assert orden.total == -50.0
    
    def test_cliente_nombre_vacio(self):
        """Debe manejar nombre de cliente vacío."""
        orden = Orden(
            id=1,
            mesa_id=1,
            cliente_nombre="",
            estado="abierta",
            total=0.0,
            fecha=datetime.now()
        )
        
        assert orden.cliente_nombre == ""
