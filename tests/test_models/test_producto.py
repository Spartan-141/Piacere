"""
Tests para el modelo Producto.
"""
import pytest
from app.models.producto import Producto


class TestProductoCreacion:
    """Tests de creación del modelo Producto."""
    
    def test_crear_producto_completo(self):
        """Debe crear un producto con todos los campos."""
        producto = Producto(
            id=1,
            nombre="Coca Cola",
            descripcion="Refresco 500ml",
            stock=100,
            precio=2.50
        )
        
        assert producto.id == 1
        assert producto.nombre == "Coca Cola"
        assert producto.descripcion == "Refresco 500ml"
        assert producto.stock == 100
        assert producto.precio == 2.50
    
    def test_crear_producto_sin_descripcion(self):
        """Debe crear un producto sin descripción."""
        producto = Producto(
            id=1,
            nombre="Producto",
            descripcion=None,
            stock=50,
            precio=10.0
        )
        
        assert producto.descripcion is None
    
    def test_crear_producto_sin_id(self):
        """Debe crear producto sin ID (para nuevos productos)."""
        producto = Producto(
            id=None,
            nombre="Nuevo",
            descripcion="Test",
            stock=10,
            precio=5.0
        )
        
        assert producto.id is None


class TestProductoStock:
    """Tests de gestión de stock."""
    
    def test_tiene_stock_suficiente(self):
        """Debe verificar stock suficiente."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=100, precio=1.0)
        
        assert producto.tiene_stock(50) == True
        assert producto.tiene_stock(100) == True
    
    def test_tiene_stock_insuficiente(self):
        """Debe detectar stock insuficiente."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=10, precio=1.0)
        
        assert producto.tiene_stock(11) == False
        assert producto.tiene_stock(100) == False
    
    def test_tiene_stock_default(self):
        """Debe verificar stock de 1 por defecto."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=5, precio=1.0)
        
        assert producto.tiene_stock() == True
    
    def test_tiene_stock_cero(self):
        """Producto sin stock debe retornar False."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=0, precio=1.0)
        
        assert producto.tiene_stock(1) == False
    
    def test_reducir_stock_exitoso(self):
        """Debe reducir stock correctamente."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=100, precio=1.0)
        
        resultado = producto.reducir_stock(30)
        
        assert resultado == True
        assert producto.stock == 70
    
    def test_reducir_stock_fallido(self):
        """No debe reducir si no hay stock suficiente."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=10, precio=1.0)
        
        resultado = producto.reducir_stock(20)
        
        assert resultado == False
        assert producto.stock == 10  # No cambió
    
    def test_reducir_stock_a_cero(self):
        """Debe poder reducir stock a cero."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=50, precio=1.0)
        
        resultado = producto.reducir_stock(50)
        
        assert resultado == True
        assert producto.stock == 0
    
    def test_aumentar_stock(self):
        """Debe aumentar stock correctamente."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=50, precio=1.0)
        
        producto.aumentar_stock(25)
        
        assert producto.stock == 75
    
    def test_aumentar_stock_desde_cero(self):
        """Debe poder aumentar desde stock cero."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=0, precio=1.0)
        
        producto.aumentar_stock(100)
        
        assert producto.stock == 100


class TestProductoFormato:
    """Tests de métodos de formateo."""
    
    def test_get_precio_formateado(self):
        """Debe formatear precio correctamente."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=10, precio=12.50)
        
        assert producto.get_precio_formateado() == "$12.50"
    
    def test_get_precio_formateado_entero(self):
        """Debe formatear precios enteros con .00."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=10, precio=10.0)
        
        assert producto.get_precio_formateado() == "$10.00"
    
    def test_str_representation(self):
        """Debe tener representación string correcta."""
        producto = Producto(id=1, nombre="Coca Cola", descripcion=None, stock=50, precio=2.50)
        
        assert str(producto) == "Coca Cola (Stock: 50)"


class TestProductoFixture:
    """Tests usando fixture."""
    
    def test_usar_fixture_producto(self, producto_refresco):
        """Debe usar correctamente la fixture de producto."""
        assert producto_refresco.nombre == "Coca Cola"
        assert producto_refresco.stock == 100
        assert producto_refresco.precio == 2.50


class TestProductoEdgeCases:
    """Tests de casos extremos."""
    
    def test_stock_negativo_inicial(self):
        """Debe permitir crear producto con stock negativo (para ajustes)."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=-10, precio=1.0)
        
        assert producto.stock == -10
    
    def test_precio_cero(self):
        """Debe permitir precio cero (productos gratis)."""
        producto = Producto(id=1, nombre="Gratis", descripcion=None, stock=10, precio=0.0)
        
        assert producto.precio == 0.0
        assert producto.get_precio_formateado() == "$0.00"
    
    def test_stock_muy_alto(self):
        """Debe manejar stock muy alto."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=1000000, precio=1.0)
        
        assert producto.tiene_stock(999999) == True
    
    def test_reducir_aumentar_multiples_veces(self):
        """Debe manejar múltiples operaciones de stock."""
        producto = Producto(id=1, nombre="Test", descripcion=None, stock=100, precio=1.0)
        
        producto.reducir_stock(20)  # 80
        producto.aumentar_stock(30)  # 110
        producto.reducir_stock(10)  # 100
        
        assert producto.stock == 100
