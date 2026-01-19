# src/app/services/inventario_service.py
from typing import List, Optional, Tuple
import sqlite3

from ..db.connection import ConnectionManager
from ..models import Producto


def obtener_productos() -> List[Producto]:
    """
    Devuelve lista de productos como objetos Producto.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos ORDER BY nombre")
        rows = cur.fetchall()
        return [Producto(*row) for row in rows]


def obtener_producto_por_id(producto_id: int) -> Optional[Producto]:
    """
    Obtiene un producto por ID.
    Retorna un objeto Producto o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos WHERE id = ?", (producto_id,))
        row = cur.fetchone()
        return Producto(*row) if row else None


def crear_producto(nombre: str, precio: float, stock: int) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Crea un producto.
    Retorna (ok, error, producto_id).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                (nombre, float(precio), int(stock))
            )
            return True, None, cur.lastrowid
    except sqlite3.IntegrityError as e:
        return False, str(e), None
    except Exception as e:
        return False, str(e), None


def actualizar_producto(producto_id: int, nombre: str, precio: float, stock: int) -> Tuple[bool, Optional[str]]:
    """
    Actualiza un producto.
    Retorna (ok, error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?",
                (nombre, float(precio), int(stock), producto_id)
            )
            return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def eliminar_producto(producto_id: int) -> Tuple[bool, Optional[str]]:
    """
    Elimina un producto.
    Retorna (ok, error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            # Verificación defensiva: evitar eliminar producto referenciado en ordenes
            try:
                cur.execute("SELECT COUNT(*) FROM orden_detalles WHERE producto_id = ?", (producto_id,))
                if cur.fetchone()[0] > 0:
                    return False, "El producto está referenciado en órdenes y no puede eliminarse"
            except Exception:
                # si la tabla no existe o falla la comprobación, continuamos con la eliminación
                pass
            cur.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            return True, None
    except Exception as e:
        return False, str(e)


def ajustar_stock(producto_id: int, cantidad: int) -> Tuple[bool, Optional[str]]:
    """
    Ajusta el stock de un producto (suma o resta).
    Retorna (ok, error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE productos SET stock = stock + ? WHERE id = ?",
                (cantidad, producto_id)
            )
            # Verificar que el stock no sea negativo
            cur.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
            row = cur.fetchone()
            if row and row[0] < 0:
                conn.rollback()
                return False, "El stock no puede ser negativo"
            return True, None
    except Exception as e:
        return False, str(e)