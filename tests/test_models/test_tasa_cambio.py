"""
Tests para el modelo TasaCambio.
"""
import pytest
import datetime
from app.models.tasa_cambio import TasaCambio


class TestTasaCambioCreacion:
    """Tests de creación del modelo TasaCambio."""
    
    def test_crear_tasa_cambio_valida(self):
        """Debe crear una tasa de cambio con valores válidos."""
        tasa = TasaCambio(id=1, fecha=datetime.date(2024, 1, 15), tasa=42.50)
        
        assert tasa.id == 1
        assert tasa.fecha == datetime.date(2024, 1, 15)
        assert tasa.tasa == 42.50
    
    def test_crear_tasa_con_fecha_hoy(self):
        """Debe crear una tasa con la fecha de hoy."""
        hoy = datetime.date.today()
        tasa = TasaCambio(id=1, fecha=hoy, tasa=40.0)
        
        assert tasa.fecha == hoy
        assert tasa.tasa == 40.0
    
    def test_crear_tasa_con_decimales(self):
        """Debe manejar correctamente tasas con decimales."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.567)
        
        assert tasa.tasa == 42.567
    
    def test_crear_tasa_sin_id(self):
        """Debe crear tasa sin ID (para nuevas tasas)."""
        tasa = TasaCambio(id=None, fecha=datetime.date.today(), tasa=42.50)
        
        assert tasa.id is None


class TestTasaCambioConversion:
    """Tests de métodos de conversión."""
    
    def test_convertir_a_bolivares_basico(self):
        """Debe convertir USD a VES correctamente."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=40.0)
        resultado = tasa.convertir_a_bolivares(100.0)
        
        assert resultado == 4000.0
    
    def test_convertir_a_bolivares_con_decimales(self):
        """Debe manejar conversiones con decimales."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.50)
        resultado = tasa.convertir_a_bolivares(10.5)
        
        assert resultado == pytest.approx(446.25, rel=1e-2)
    
    def test_convertir_a_bolivares_cero(self):
        """Debe manejar conversión de cero."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.50)
        resultado = tasa.convertir_a_bolivares(0.0)
        
        assert resultado == 0.0
    
    def test_convertir_a_dolares_basico(self):
        """Debe convertir VES a USD correctamente."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=40.0)
        resultado = tasa.convertir_a_dolares(4000.0)
        
        assert resultado == 100.0
    
    def test_convertir_a_dolares_con_decimales(self):
        """Debe manejar conversiones inversas con decimales."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.50)
        resultado = tasa.convertir_a_dolares(446.25)
        
        assert resultado == pytest.approx(10.5, rel=1e-2)
    
    def test_convertir_a_dolares_cero(self):
        """Debe manejar conversión de cero."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.50)
        resultado = tasa.convertir_a_dolares(0.0)
        
        assert resultado == 0.0
    
    def test_convertir_a_dolares_tasa_cero(self):
        """Debe manejar división por cero cuando tasa es 0."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=0.0)
        resultado = tasa.convertir_a_dolares(100.0)
        
        assert resultado == 0.0
    
    def test_conversion_ida_y_vuelta(self):
        """La conversión USD->VES->USD debe ser consistente."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.50)
        monto_original = 100.0
        
        bolivares = tasa.convertir_a_bolivares(monto_original)
        dolares = tasa.convertir_a_dolares(bolivares)
        
        assert dolares == pytest.approx(monto_original, rel=1e-2)


class TestTasaCambioFormato:
    """Tests de métodos de formateo."""
    
    def test_get_tasa_formateada_dos_decimales(self):
        """Debe formatear la tasa con 2 decimales y prefijo Bs."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.50)
        
        assert tasa.get_tasa_formateada() == "Bs. 42.50"
    
    def test_get_tasa_formateada_redondeo(self):
        """Debe redondear correctamente a 2 decimales."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.567)
        
        assert tasa.get_tasa_formateada() == "Bs. 42.57"
    
    def test_get_tasa_formateada_entero(self):
        """Debe formatear tasas enteras con .00."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=40.0)
        
        assert tasa.get_tasa_formateada() == "Bs. 40.00"
    
    def test_str_representation(self):
        """Debe tener representación string correcta."""
        fecha = datetime.date(2024, 1, 15)
        tasa = TasaCambio(id=1, fecha=fecha, tasa=42.50)
        
        assert str(tasa) == "2024-01-15: Bs. 42.50"


class TestTasaCambioEdgeCases:
    """Tests de casos extremos."""
    
    def test_tasa_muy_alta(self):
        """Debe manejar tasas muy altas."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=1000000.0)
        resultado = tasa.convertir_a_bolivares(1.0)
        
        assert resultado == 1000000.0
    
    def test_tasa_muy_baja(self):
        """Debe manejar tasas muy bajas."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=0.01)
        resultado = tasa.convertir_a_bolivares(100.0)
        
        assert resultado == 1.0
    
    def test_monto_negativo(self):
        """Debe manejar montos negativos (aunque no sea común)."""
        tasa = TasaCambio(id=1, fecha=datetime.date.today(), tasa=42.50)
        resultado = tasa.convertir_a_bolivares(-10.0)
        
        assert resultado == -425.0


class TestTasaCambioFixture:
    """Tests usando fixture de tasa_actual."""
    
    def test_usar_fixture_tasa_actual(self, tasa_actual):
        """Debe poder usar la fixture tasa_actual."""
        assert tasa_actual.tasa == 42.50
        assert tasa_actual.fecha == datetime.date.today()
        assert tasa_actual.id == 1
    
    def test_fixture_conversion(self, tasa_actual):
        """Debe funcionar la conversión con fixture."""
        resultado = tasa_actual.convertir_a_bolivares(100.0)
        
        assert resultado == 4250.0
