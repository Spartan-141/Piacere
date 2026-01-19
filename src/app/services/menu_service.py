# src/app/services/menu_service.py
from typing import List, Optional, Tuple
import sqlite3
from ..db.connection import ConnectionManager
from ..models import MenuSection, MenuItem


# --------------------------
# Secciones (menu_section)
# --------------------------


def listar_secciones(only_active: bool = True) -> List[MenuSection]:
    """
    Devuelve lista de secciones del menú.
    Retorna objetos MenuSection en lugar de tuplas.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        if only_active:
            cur.execute(
                """SELECT id, nombre, descripcion, position, active 
                FROM menu_sections WHERE active=1 ORDER BY position, nombre"""
            )
        else:
            cur.execute(
                """SELECT id, nombre, descripcion, position, active 
                FROM menu_sections ORDER BY position, nombre"""
            )
        rows = cur.fetchall()
        return [MenuSection(*row) for row in rows]


def crear_seccion(
    nombre: str, descripcion: Optional[str] = None, position: Optional[int] = None
) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Crea una sección. Devuelve (ok, error_message, section_id).
    Si position es None, se calcula automáticamente como MAX(position) + 1.
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()

            # Si no se proporciona position, calcular automáticamente
            if position is None:
                cur.execute("SELECT MAX(position) FROM menu_sections")
                max_pos = cur.fetchone()[0]
                position = (max_pos or 0) + 1

            cur.execute(
                """INSERT INTO menu_sections(nombre, descripcion, position) 
                VALUES (?, ?, ?)""",
                (nombre, descripcion, position),
            )
            conn.commit()
            return True, None, cur.lastrowid
    except sqlite3.IntegrityError:
        return False, "Ya existe una sección con ese nombre", None
    except Exception as e:
        return False, str(e), None


def obtener_seccion_por_id(section_id: int) -> Optional[MenuSection]:
    """Obtiene una sección por ID, retorna MenuSection o None"""
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre, descripcion, position, active 
            FROM menu_sections WHERE id = ?""",
            (section_id,),
        )
        row = cur.fetchone()
        return MenuSection(*row) if row else None


def actualizar_seccion(
    section_id: int,
    nombre: str,
    descripcion: Optional[str],
    position: int,
    active: int = 1,
) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE menu_sections 
                SET nombre = ?, descripcion = ?, position = ?, active = ? 
                WHERE id = ?""",
                (nombre, descripcion, position, active, section_id),
            )
            conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Ya existe una sección con ese nombre"
    except Exception as e:
        return False, str(e)


def eliminar_seccion(section_id: int, soft: bool = True) -> Tuple[bool, Optional[str]]:
    """
    Elimina una sección.
    - Si soft=True marca active=0 (recomendado).
    - Si soft=False intenta borrado físico.
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            if soft:
                cur.execute(
                    "UPDATE menu_sections SET active = 0 WHERE id = ?", (section_id,)
                )
            else:
                cur.execute("DELETE FROM menu_sections WHERE id = ?", (section_id,))
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


# --------------------------
# Items (menu_items)
# --------------------------


def listar_items_por_seccion(
    section_id: int, only_disponible: bool = True
) -> List[MenuItem]:
    """
    Devuelve lista de items en una sección.
    Retorna objetos MenuItem en lugar de tuplas.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        if only_disponible:
            cur.execute(
                """
                SELECT id, section_id, nombre, descripcion, precio, 
                       disponible, position, created_at
                FROM menu_items
                WHERE section_id = ? AND disponible = 1
                ORDER BY position, nombre
            """,
                (section_id,),
            )
        else:
            cur.execute(
                """
                SELECT id, section_id, nombre, descripcion, precio, 
                       disponible, position, created_at
                FROM menu_items
                WHERE section_id = ?
                ORDER BY position, nombre
            """,
                (section_id,),
            )
        rows = cur.fetchall()
        return [MenuItem(*row) for row in rows]


def crear_item(
    section_id: int,
    nombre: str,
    descripcion: Optional[str],
    precio: float,
    disponible: int = 1,
    position: Optional[int] = None,
) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Crea un item en la sección indicada.
    Devuelve (ok, error_message, item_id).
    Si position es None, se calcula automáticamente.
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()

            # Si no se proporciona position, calcular automáticamente
            if position is None:
                cur.execute(
                    "SELECT MAX(position) FROM menu_items WHERE section_id = ?",
                    (section_id,),
                )
                max_pos = cur.fetchone()[0]
                position = (max_pos or 0) + 1

            cur.execute(
                """
                INSERT INTO menu_items 
                (section_id, nombre, descripcion, precio, disponible, position)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (section_id, nombre, descripcion, precio, disponible, position),
            )
            conn.commit()
            return True, None, cur.lastrowid
    except sqlite3.IntegrityError:
        return False, "Registro duplicado o error de integridad", None
    except Exception as e:
        return False, str(e), None


def obtener_item_por_id(item_id: int) -> Optional[MenuItem]:
    """Obtiene un item por ID, retorna MenuItem o None"""
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, section_id, nombre, descripcion, precio, 
                   disponible, position, created_at
            FROM menu_items WHERE id = ?
        """,
            (item_id,),
        )
        row = cur.fetchone()
        return MenuItem(*row) if row else None


def actualizar_item(
    item_id: int,
    section_id: int,
    nombre: str,
    descripcion: Optional[str],
    precio: float,
    disponible: int = 1,
    position: int = 0,
) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE menu_items
                SET section_id = ?, nombre = ?, descripcion = ?, 
                    precio = ?, disponible = ?, position = ?
                WHERE id = ?
            """,
                (
                    section_id,
                    nombre,
                    descripcion,
                    precio,
                    disponible,
                    position,
                    item_id,
                ),
            )
            conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Registro duplicado o error de integridad"
    except Exception as e:
        return False, str(e)


def eliminar_item(item_id: int) -> Tuple[bool, Optional[str]]:
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


# --------------------------
# Utilidades y helpers
# --------------------------


def toggle_disponibilidad_item(
    item_id: int, disponible: int
) -> Tuple[bool, Optional[str]]:
    """
    Cambia la disponibilidad de un ítem (1 = disponible, 0 = no disponible)
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE menu_items SET disponible = ? WHERE id = ?",
                (1 if disponible else 0, item_id),
            )
            conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)


def intercambiar_positions_items(
    item_id_1: int, item_id_2: int
) -> Tuple[bool, Optional[str]]:
    """Intercambia las posiciones de dos items"""
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()

            # Obtener positions actuales
            cur.execute("SELECT position FROM menu_items WHERE id = ?", (item_id_1,))
            pos1 = cur.fetchone()[0]

            cur.execute("SELECT position FROM menu_items WHERE id = ?", (item_id_2,))
            pos2 = cur.fetchone()[0]

            # Intercambiar
            cur.execute(
                "UPDATE menu_items SET position = ? WHERE id = ?", (pos2, item_id_1)
            )
            cur.execute(
                "UPDATE menu_items SET position = ? WHERE id = ?", (pos1, item_id_2)
            )

            conn.commit()
            return True, None
    except Exception as e:
        return False, str(e)


def buscar_items_por_nombre(term: str, only_disponible: bool = True) -> List[MenuItem]:
    """
    Búsqueda simple por nombre en todo el menú.
    Retorna objetos MenuItem en lugar de tuplas.
    """
    like = f"%{term}%"
    with ConnectionManager() as conn:
        cur = conn.cursor()
        if only_disponible:
            cur.execute(
                """
                SELECT id, section_id, nombre, descripcion, precio, 
                       disponible, position, created_at
                FROM menu_items
                WHERE nombre LIKE ? AND disponible = 1
                ORDER BY section_id, position, nombre
            """,
                (like,),
            )
        else:
            cur.execute(
                """
                SELECT id, section_id, nombre, descripcion, precio, 
                       disponible, position, created_at
                FROM menu_items
                WHERE nombre LIKE ?
                ORDER BY section_id, position, nombre
            """,
                (like,),
            )
        rows = cur.fetchall()
        return [MenuItem(*row) for row in rows]
