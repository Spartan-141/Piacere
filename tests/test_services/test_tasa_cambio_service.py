"""
Tests para tasa_cambio_service.
"""
import pytest
import sqlite3
from datetime import date, datetime
from unittest.mock import patch, MagicMock
from app.services import tasa_cambio_service
from app.models.tasa_cambio import TasaCambio


@pytest.fixture
def db_conn(db_memory):
    """
    Fixture que proporciona una conexión de BD en memoria.
    Mockea ConnectionManager para usar esta conexión.
    """
    with patch('app.services.tasa_cambio_service.ConnectionManager') as mock_cm:
        mock_cm.return_value.__enter__.return_value = db_memory
        mock_cm.return_value.__exit__.return_value = None
        yield db_memory


class TestGuardarTasa:
    """Tests de guardar_tasa."""
    
    def test_guardar_tasa_nueva(self, db_conn):
        """Debe guardar una tasa nueva correctamente."""
        fecha = "2024-01-15"
        tasa = 42.50
        
        ok, error = tasa_cambio_service.guardar_tasa(fecha, tasa)
        
        assert ok == True
        assert error is None
        
        # Verificar que se guardó
        cursor = db_conn.cursor()
        cursor.execute("SELECT fecha, tasa FROM tasas_cambio WHERE fecha = ?", (fecha,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == fecha
        assert row[1] == tasa
    
    def test_guardar_tasa_actualiza_existente(self, db_conn):
        """Debe actualizar una tasa existente."""
        fecha = "2024-01-15"
        
        # Guardar tasa inicial
        tasa_cambio_service.guardar_tasa(fecha, 40.0)
        
        # Actualizar
        ok, error = tasa_cambio_service.guardar_tasa(fecha, 45.0)
        
        assert ok == True
        assert error is None
        
        # Verificar que se actualizó
        cursor = db_conn.cursor()
        cursor.execute("SELECT tasa FROM tasas_cambio WHERE fecha = ?", (fecha,))
        row = cursor.fetchone()
        assert row[0] == 45.0


class TestObtenerTasa:
    """Tests de obtener_tasa."""
    
    def test_obtener_tasa_existente(self, db_conn):
        """Debe obtener una tasa existente."""
        fecha = "2024-01-15"
        tasa_valor = 42.50
        
        # Insertar tasa
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", (fecha, tasa_valor))
        db_conn.commit()
        
        # Obtener
        tasa = tasa_cambio_service.obtener_tasa(fecha)
        
        assert tasa is not None
        assert isinstance(tasa, TasaCambio)
        assert str(tasa.fecha) == fecha
        assert tasa.tasa == tasa_valor
    
    def test_obtener_tasa_no_existente(self, db_conn):
        """Debe retornar None si la tasa no existe."""
        tasa = tasa_cambio_service.obtener_tasa("2099-12-31")
        
        assert tasa is None


class TestConversiones:
    """Tests de conversiones USD/VES."""
    
    def test_usd_a_ves_exitoso(self, db_conn):
        """Debe convertir USD a VES correctamente."""
        fecha = "2024-01-15"
        
        # Insertar tasa
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", (fecha, 40.0))
        db_conn.commit()
        
        # Convertir
        resultado = tasa_cambio_service.usd_a_ves(100.0, fecha)
        
        assert resultado == 4000.0
    
    def test_usd_a_ves_sin_tasa(self, db_conn):
        """Debe retornar None si no hay tasa."""
        resultado = tasa_cambio_service.usd_a_ves(100.0, "2099-12-31")
        
        assert resultado is None
    
    def test_ves_a_usd_exitoso(self, db_conn):
        """Debe convertir VES a USD correctamente."""
        fecha = "2024-01-15"
        
        # Insertar tasa
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", (fecha, 40.0))
        db_conn.commit()
        
        # Convertir
        resultado = tasa_cambio_service.ves_a_usd(4000.0, fecha)
        
        assert resultado == 100.0
    
    def test_ves_a_usd_sin_tasa(self, db_conn):
        """Debe retornar None si no hay tasa."""
        resultado = tasa_cambio_service.ves_a_usd(4000.0, "2099-12-31")
        
        assert resultado is None


class TestListarTasas:
    """Tests de listar_tasas."""
    
    def test_listar_tasas_varias(self, db_conn):
        """Debe listar todas las tasas ordenadas por fecha DESC."""
        # Insertar varias tasas
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", ("2024-01-15", 42.0))
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", ("2024-01-16", 43.0))
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", ("2024-01-14", 41.0))
        db_conn.commit()
        
        # Listar
        tasas = tasa_cambio_service.listar_tasas()
        
        assert len(tasas) == 3
        assert all(isinstance(t, TasaCambio) for t in tasas)
        # Debe estar ordenado por fecha DESC
        assert str(tasas[0].fecha) == "2024-01-16"
        assert str(tasas[1].fecha) == "2024-01-15"
        assert str(tasas[2].fecha) == "2024-01-14"
    
    def test_listar_tasas_vacio(self, db_conn):
        """Debe retornar lista vacía si no hay tasas."""
        tasas = tasa_cambio_service.listar_tasas()
        
        assert tasas == []


class TestEliminarTasa:
    """Tests de eliminar_tasa."""
    
    def test_eliminar_tasa_existente(self, db_conn):
        """Debe eliminar una tasa existente."""
        fecha = "2024-01-15"
        
        # Insertar tasa
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", (fecha, 42.0))
        db_conn.commit()
        
        # Eliminar
        ok, error = tasa_cambio_service.eliminar_tasa(fecha)
        
        assert ok == True
        assert error is None
        
        # Verificar que se eliminó
        cursor.execute("SELECT * FROM tasas_cambio WHERE fecha = ?", (fecha,))
        assert cursor.fetchone() is None
    
    def test_eliminar_tasa_no_existente(self, db_conn):
        """Debe retornar ok=True aunque la tasa no exista."""
        ok, error = tasa_cambio_service.eliminar_tasa("2099-12-31")
        
        assert ok == True
        assert error is None


class TestActualizarTasa:
    """Tests de actualizar_tasa."""
    
    def test_actualizar_tasa_existente(self, db_conn):
        """Debe actualizar una tasa existente."""
        fecha = "2024-01-15"
        
        # Insertar tasa
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", (fecha, 40.0))
        db_conn.commit()
        
        # Actualizar
        ok, error = tasa_cambio_service.actualizar_tasa(fecha, 45.0)
        
        assert ok == True
        assert error is None
        
        # Verificar actualización
        cursor.execute("SELECT tasa FROM tasas_cambio WHERE fecha = ?", (fecha,))
        row = cursor.fetchone()
        assert row[0] == 45.0
    
    def test_actualizar_tasa_no_existente(self, db_conn):
        """Debe retornar ok=True aunque la tasa no exista (no hace nada)."""
        ok, error = tasa_cambio_service.actualizar_tasa("2099-12-31", 50.0)
        
        assert ok == True
        assert error is None


class TestObtenerTasaDelDia:
    """Tests de obtener_tasa_del_dia."""
    
    def test_obtener_tasa_mas_reciente(self, db_conn):
        """Debe obtener la tasa más reciente."""
        # Insertar varias tasas
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", ("2024-01-14", 41.0))
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", ("2024-01-16", 43.0))
        cursor.execute("INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", ("2024-01-15", 42.0))
        db_conn.commit()
        
        # Obtener tasa del día (más reciente)
        tasa = tasa_cambio_service.obtener_tasa_del_dia()
        
        assert tasa is not None
        assert str(tasa.fecha) == "2024-01-16"
        assert tasa.tasa == 43.0
    
    def test_obtener_tasa_del_dia_sin_tasas(self, db_conn):
        """Debe retornar None si no hay tasas."""
        tasa = tasa_cambio_service.obtener_tasa_del_dia()
        
        assert tasa is None
