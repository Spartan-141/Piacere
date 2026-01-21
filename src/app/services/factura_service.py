from ..db.connection import ConnectionManager
from ..models import Factura
from typing import List, Optional, Tuple


def obtener_facturas_rango(fecha_inicio: str, fecha_fin: str) -> List[Factura]:
    """
    Devuelve lista de facturas entre dos fechas como objetos Factura.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, orden_id, numero_factura, fecha, cliente_nombre, forma_pago, total, total_ves
            FROM facturas
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        """,
            (fecha_inicio, fecha_fin),
        )
        rows = cur.fetchall()
        return [Factura(*row) for row in rows]


def buscar_facturas(termino: str) -> List[Factura]:
    """
    Busca facturas por número O por nombre de cliente.
    Retorna objetos Factura.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        param = f"%{termino}%"
        cur.execute(
            """
            SELECT id, orden_id, numero_factura, fecha, cliente_nombre, forma_pago, total, total_ves
            FROM facturas
            WHERE cliente_nombre LIKE ? OR numero_factura LIKE ?
            ORDER BY fecha DESC
        """,
            (param, param),
        )
        rows = cur.fetchall()
        return [Factura(*row) for row in rows]


def obtener_factura_por_id(factura_id: int) -> Optional[Factura]:
    """
    Obtiene una factura por ID.
    Retorna un objeto Factura o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, orden_id, numero_factura, fecha, cliente_nombre, forma_pago, total, total_ves
            FROM facturas
            WHERE id = ?
        """,
            (factura_id,),
        )
        row = cur.fetchone()
        return Factura(*row) if row else None


def eliminar_factura(factura_id: int) -> Tuple[bool, Optional[str]]:
    """
    Elimina una factura y sus detalles asociados.
    Retorna (ok, error_msg).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            # obtener orden asociada
            cur.execute("SELECT orden_id FROM facturas WHERE id = ?", (factura_id,))
            row = cur.fetchone()
            if not row:
                return False, "Factura no encontrada"
            orden_id = row[0]

            # eliminar detalles de la orden
            cur.execute("DELETE FROM orden_detalles WHERE orden_id = ?", (orden_id,))
            # eliminar la orden
            cur.execute("DELETE FROM ordenes WHERE id = ?", (orden_id,))
            # eliminar la factura
            cur.execute("DELETE FROM facturas WHERE id = ?", (factura_id,))

            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


def obtener_detalles_factura(factura_id: int) -> List[Tuple]:
    """
    Devuelve detalles de una factura.
    Cada fila: (producto, variante, cantidad, precio_unitario, subtotal, cliente_nombre)
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                mi.nombre AS producto,
                COALESCE(v.nombre, '') AS variante,
                d.cantidad,
                COALESCE(d.precio_unitario, d.precio) AS precio_unitario,
                d.subtotal,
                f.cliente_nombre
            FROM facturas f
            JOIN ordenes o ON f.orden_id = o.id
            JOIN orden_detalles d ON o.id = d.orden_id
            LEFT JOIN menu_items mi ON d.menu_item_id = mi.id
            LEFT JOIN menu_item_variant v ON d.variant_id = v.id
            WHERE f.id = ?
            ORDER BY d.id
        """,
            (factura_id,),
        )
        return cur.fetchall()


def listar_todas_facturas() -> List[Factura]:
    """
    Lista todas las facturas ordenadas por fecha descendente.
    Retorna objetos Factura.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, orden_id, numero_factura, fecha, cliente_nombre, forma_pago, total, total_ves
            FROM facturas
            ORDER BY fecha DESC
        """
        )
        rows = cur.fetchall()
        return [Factura(*row) for row in rows]
