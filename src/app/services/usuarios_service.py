# src/app/services/usuarios_service.py
from typing import List, Optional, Tuple
import hashlib
import sqlite3

from ..db.connection import ConnectionManager
from ..models import Usuario


def obtener_usuarios() -> List[Usuario]:
    """
    Devuelve lista de usuarios como objetos Usuario.
    (omitimos la clave en la respuesta por seguridad).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, apellido, usuario, clave, rol FROM usuarios ORDER BY id")
        rows = cur.fetchall()
    
    return [Usuario(*row) for row in rows]


def obtener_usuario_por_id(usuario_id: int) -> Optional[Usuario]:
    """
    Devuelve un objeto Usuario o None si no existe.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, apellido, usuario, clave, rol FROM usuarios WHERE id = ?", (usuario_id,))
        row = cur.fetchone()
    
    return Usuario(*row) if row else None


def obtener_usuario_por_username(username: str) -> Optional[Usuario]:
    """
    Devuelve un objeto Usuario por nombre de usuario o None si no existe.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, apellido, usuario, clave, rol FROM usuarios WHERE usuario = ?", (username,))
        row = cur.fetchone()
    
    return Usuario(*row) if row else None


def registrar_usuario(nombre: str, apellido: str, usuario: str, clave: str, rol: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Registra un usuario nuevo.
    Devuelve (ok, mensaje_error, usuario_id).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
            if cur.fetchone()[0] > 0:
                return False, "El nombre de usuario ya existe", None
            cur.execute(
                "INSERT INTO usuarios (nombre, apellido, usuario, clave, rol) VALUES (?, ?, ?, ?, ?)",
                (nombre, apellido, usuario, clave, rol)
            )
            return True, None, cur.lastrowid
    except sqlite3.IntegrityError as e:
        return False, str(e), None
    except Exception as e:
        return False, str(e), None


def actualizar_usuario(usuario_id: int, nombre: str, apellido: str, usuario: str, clave: Optional[str], rol: str) -> Tuple[bool, Optional[str]]:
    """
    Actualiza un usuario. Si `clave` es None o cadena vacía, no la modifica.
    Devuelve (ok, mensaje_error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ? AND id != ?", (usuario, usuario_id))
            if cur.fetchone()[0] > 0:
                return False, "El nombre de usuario ya está en uso por otro usuario"
            if clave:
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, apellido = ?, usuario = ?, clave = ?, rol = ? WHERE id = ?",
                    (nombre, apellido, usuario, clave, rol, usuario_id)
                )
            else:
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, apellido = ?, usuario = ?, rol = ? WHERE id = ?",
                    (nombre, apellido, usuario, rol, usuario_id)
                )
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def eliminar_usuario_por_id(usuario_id: int) -> Tuple[bool, Optional[str]]:
    """
    Elimina un usuario por id. Devuelve (ok, mensaje_error).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        return True, None
    except Exception as e:
        return False, str(e)