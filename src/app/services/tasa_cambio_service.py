from ..db.connection import ConnectionManager
from ..models import TasaCambio
from typing import Optional, List, Tuple
from datetime import date


def guardar_tasa(fecha: str, tasa: float) -> Tuple[bool, Optional[str]]:
    """
    Guarda o actualiza una tasa de cambio.
    Retorna (ok, error).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT OR REPLACE INTO tasas_cambio (fecha, tasa) VALUES (?, ?)", (fecha, tasa))
            return True, None
        except Exception as e:
            return False, str(e)


def obtener_tasa(fecha: str) -> Optional[TasaCambio]:
    """
    Obtiene la tasa de cambio para una fecha específica.
    Retorna un objeto TasaCambio o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, fecha, tasa FROM tasas_cambio WHERE fecha = ?", (fecha,))
        row = cur.fetchone()
        return TasaCambio(*row) if row else None


def usd_a_ves(monto_usd: float, fecha: str) -> Optional[float]:
    """
    Convierte USD a VES usando la tasa de la fecha especificada.
    """
    tasa_obj = obtener_tasa(fecha)
    if tasa_obj is None:
        return None
    return tasa_obj.convertir_a_bolivares(monto_usd)


def ves_a_usd(monto_ves: float, fecha: str) -> Optional[float]:
    """
    Convierte VES a USD usando la tasa de la fecha especificada.
    """
    tasa_obj = obtener_tasa(fecha)
    if tasa_obj is None:
        return None
    return tasa_obj.convertir_a_dolares(monto_ves)


def listar_tasas() -> List[TasaCambio]:
    """
    Lista todas las tasas de cambio ordenadas por fecha descendente.
    Retorna lista de objetos TasaCambio.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, fecha, tasa FROM tasas_cambio ORDER BY fecha DESC")
        rows = cur.fetchall()
        return [TasaCambio(*row) for row in rows]

    
def eliminar_tasa(fecha: str) -> Tuple[bool, Optional[str]]:
    """
    Elimina una tasa de cambio por fecha.
    Retorna (ok, error).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM tasas_cambio WHERE fecha = ?", (fecha,))
            return True, None
        except Exception as e:
            return False, str(e)

        
def actualizar_tasa(fecha: str, nueva_tasa: float) -> Tuple[bool, Optional[str]]:
    """
    Actualiza una tasa de cambio existente.
    Retorna (ok, error).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        try:
            cur.execute("UPDATE tasas_cambio SET tasa = ? WHERE fecha = ?", (nueva_tasa, fecha))
            return True, None
        except Exception as e:
            return False, str(e)

        
def obtener_tasa_del_dia() -> Optional[TasaCambio]:
    """
    Devuelve la tasa más reciente registrada en la base de datos.
    Retorna un objeto TasaCambio o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, fecha, tasa FROM tasas_cambio ORDER BY fecha DESC LIMIT 1")
        row = cur.fetchone()
        return TasaCambio(*row) if row else None


def obtener_tasa_actual() -> Optional[float]:
    """
    Devuelve solo el valor de la tasa más reciente.
    Retorna float o None.
    """
    tasa = obtener_tasa_del_dia()
    return tasa.tasa if tasa else None