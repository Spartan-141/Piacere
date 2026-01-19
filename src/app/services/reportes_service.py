# src/app/services/reportes_service.py
from typing import List, Tuple
from ..db.connection import ConnectionManager


# ==========================================
# REPORTES DE VENTAS
# ==========================================


def obtener_ventas_por_periodo(
    fecha_inicio: str, fecha_fin: str
) -> Tuple[float, float, int, float]:
    """
    Obtiene métricas de ventas para un período.

    Returns:
        Tuple[total_usd, total_ves, num_ordenes, ticket_promedio]
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()

        # Total en USD y número de órdenes
        cur.execute(
            """
            SELECT
                COALESCE(SUM(total), 0) as total_usd,
                COUNT(*) as num_ordenes
            FROM ordenes
            WHERE DATE(fecha) BETWEEN ? AND ?
            AND estado IN ('abierta', 'cerrada')
            """,
            (fecha_inicio, fecha_fin),
        )
        row = cur.fetchone()
        total_usd = row[0] if row else 0.0
        num_ordenes = row[1] if row else 0

        # Total en VES (de facturas)
        cur.execute(
            """
            SELECT COALESCE(SUM(total_ves), 0) as total_ves
            FROM facturas
            WHERE DATE(fecha) BETWEEN ? AND ?
            """,
            (fecha_inicio, fecha_fin),
        )
        total_ves = cur.fetchone()[0] or 0.0

        # Ticket promedio
        ticket_promedio = total_usd / num_ordenes if num_ordenes > 0 else 0.0

        return total_usd, total_ves, num_ordenes, ticket_promedio


def obtener_ventas_diarias(fecha_inicio: str, fecha_fin: str) -> List[Tuple]:
    """
    Obtiene ventas agrupadas por día.

    Returns:
        List[Tuple[fecha, total_usd, num_ordenes]]
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                DATE(fecha) as fecha,
                COALESCE(SUM(total), 0) as total_usd,
                COUNT(*) as num_ordenes
            FROM ordenes
            WHERE DATE(fecha) BETWEEN ? AND ?
            AND estado IN ('abierta', 'cerrada')
            GROUP BY DATE(fecha)
            ORDER BY fecha DESC
            """,
            (fecha_inicio, fecha_fin),
        )
        return cur.fetchall()


# ==========================================
# REPORTES DE PRODUCTOS (MENU ITEMS)
# ==========================================


def obtener_productos_mas_vendidos(
    fecha_inicio: str, fecha_fin: str, limit: int = 10
) -> List[Tuple]:
    """
    Obtiene los items del menú más vendidos por cantidad.

    Returns:
        List[Tuple[item_nombre, cantidad_vendida, ingresos_totales]]
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                mi.nombre as item,
                SUM(od.cantidad) as cantidad_vendida,
                SUM(od.subtotal) as ingresos_totales
            FROM orden_detalles od
            JOIN ordenes o ON od.orden_id = o.id
            JOIN menu_items mi ON od.menu_item_id = mi.id
            WHERE DATE(o.fecha) BETWEEN ? AND ?
            AND o.estado IN ('abierta', 'cerrada')
            GROUP BY mi.id, mi.nombre
            ORDER BY cantidad_vendida DESC
            LIMIT ?
            """,
            (fecha_inicio, fecha_fin, limit),
        )
        return cur.fetchall()


def obtener_productos_por_ingresos(
    fecha_inicio: str, fecha_fin: str, limit: int = 10
) -> List[Tuple]:
    """
    Obtiene los items del menú que más ingresos generan.

    Returns:
        List[Tuple[item_nombre, cantidad_vendida, ingresos_totales]]
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                mi.nombre as item,
                SUM(od.cantidad) as cantidad_vendida,
                SUM(od.subtotal) as ingresos_totales
            FROM orden_detalles od
            JOIN ordenes o ON od.orden_id = o.id
            JOIN menu_items mi ON od.menu_item_id = mi.id
            WHERE DATE(o.fecha) BETWEEN ? AND ?
            AND o.estado IN ('abierta', 'cerrada')
            GROUP BY mi.id, mi.nombre
            ORDER BY ingresos_totales DESC
            LIMIT ?
            """,
            (fecha_inicio, fecha_fin, limit),
        )
        return cur.fetchall()


def calcular_total_ingresos(fecha_inicio: str, fecha_fin: str) -> float:
    """
    Calcula el total de ingresos para calcular porcentajes.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(SUM(od.subtotal), 0)
            FROM orden_detalles od
            JOIN ordenes o ON od.orden_id = o.id
            WHERE DATE(o.fecha) BETWEEN ? AND ?
            AND o.estado IN ('abierta', 'cerrada')
            """,
            (fecha_inicio, fecha_fin),
        )
        return cur.fetchone()[0] or 0.0


# ==========================================
# UTILIDADES
# ==========================================


def formatear_moneda(valor: float) -> str:
    """Formatea un valor como moneda USD"""
    return f"${valor:,.2f}"


def formatear_bolivares(valor: float) -> str:
    """Formatea un valor como bolívares"""
    return f"{valor:,.2f} Bs"


def calcular_porcentaje(parte: float, total: float) -> float:
    """Calcula el porcentaje de una parte respecto al total"""
    return (parte / total * 100) if total > 0 else 0.0
