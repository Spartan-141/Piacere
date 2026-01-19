# src/app/services/dashboard_service.py
"""
Servicio para obtener datos del dashboard.
Proporciona métricas, estadísticas y datos para visualización.
"""
from typing import Dict, List, Tuple
from datetime import datetime
from ..db.connection import ConnectionManager
from . import tasa_cambio_service


def get_current_exchange_rate() -> float:
    """
    Obtiene la tasa de cambio actual del día.
    Retorna el valor de la tasa o 0.0 si no existe.
    """
    tasa_obj = tasa_cambio_service.obtener_tasa_del_dia()
    return tasa_obj.tasa if tasa_obj else 0.0


def get_today_orders_count() -> int:
    """
    Cuenta el número de órdenes creadas hoy.
    Retorna el total de órdenes del día.
    """
    today = datetime.now().date().isoformat()

    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) 
            FROM ordenes 
            WHERE DATE(fecha) = ?
        """,
            (today,),
        )
        result = cur.fetchone()
        return result[0] if result else 0


def get_today_sales() -> Dict[str, float]:
    """
    Obtiene las ventas totales del día en USD y VES.
    Retorna dict con {usd: float, ves: float}
    """
    today = datetime.now().date().isoformat()

    with ConnectionManager() as conn:
        cur = conn.cursor()
        # Sumar totales de facturas del día
        cur.execute(
            """
            SELECT 
                COALESCE(SUM(total), 0) as total_usd,
                COALESCE(SUM(total_ves), 0) as total_ves
            FROM facturas
            WHERE DATE(fecha) = ?
        """,
            (today,),
        )
        result = cur.fetchone()

        if result:
            return {"usd": float(result[0]), "ves": float(result[1])}
        return {"usd": 0.0, "ves": 0.0}


def get_monthly_sales(months: int = 12) -> List[Tuple[str, float]]:
    """
    Obtiene las ventas mensuales de los últimos N meses.
    Retorna lista de tuplas (mes, total_ventas)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()

        # Obtener ventas agrupadas por mes
        cur.execute(
            """
            SELECT 
                strftime('%Y-%m', fecha) as mes,
                COALESCE(SUM(total), 0) as total
            FROM facturas
            WHERE fecha >= date('now', '-12 months')
            GROUP BY mes
            ORDER BY mes ASC
        """
        )

        results = cur.fetchall()

        # Convertir a formato legible
        monthly_data = []
        for mes_str, total in results:
            # Convertir "2024-11" a "Nov"
            try:
                date_obj = datetime.strptime(mes_str, "%Y-%m")
                mes_nombre = date_obj.strftime("%b")
                monthly_data.append((mes_nombre, float(total)))
            except Exception:
                monthly_data.append((mes_str, float(total)))

        return monthly_data


def get_table_status() -> Dict[str, int]:
    """
    Obtiene el estado actual de las mesas.
    Retorna dict con {libre: int, ocupada: int, reservada: int}
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()

        # Contar mesas por estado
        cur.execute(
            """
            SELECT 
                estado,
                COUNT(*) as total
            FROM mesas
            GROUP BY estado
        """
        )

        results = cur.fetchall()

        # Inicializar contadores
        status = {"libre": 0, "ocupado": 0, "reservada": 0}

        # Llenar con datos reales
        for estado, total in results:
            estado_lower = estado.lower()
            if estado_lower in status:
                status[estado_lower] = total

        return status


def get_recent_invoices(limit: int = 5) -> List[Dict]:
    """
    Obtiene las últimas N facturas.
    Retorna lista de dicts con información de cada factura.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT 
                numero_factura,
                cliente_nombre,
                total,
                fecha
            FROM facturas
            ORDER BY fecha DESC
            LIMIT ?
        """,
            (limit,),
        )

        results = cur.fetchall()

        invoices = []
        for numero, cliente, total, fecha in results:
            # Extraer solo la hora de la fecha
            try:
                fecha_obj = datetime.fromisoformat(fecha.replace(" ", "T"))
                hora = fecha_obj.strftime("%H:%M")
            except Exception:
                hora = "N/A"

            invoices.append(
                {
                    "numero": numero,
                    "cliente": cliente,
                    "monto": f"${total:.2f}",
                    "hora": hora,
                }
            )

        return invoices


def get_dashboard_summary() -> Dict:
    """
    Obtiene un resumen completo de todos los datos del dashboard.
    Útil para actualizar todo de una vez.
    """
    return {
        "tasa": get_current_exchange_rate(),
        "ordenes_hoy": get_today_orders_count(),
        "ventas_hoy": get_today_sales(),
        "ventas_mensuales": get_monthly_sales(),
        "estado_mesas": get_table_status(),
        "ultimas_facturas": get_recent_invoices(),
    }


def obtener_usuario_logeado():
    """
    Devuelve el nombre del usuario actualmente logeado.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT nombre FROM usuarios WHERE logeado = 1 LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else "Invitado"
