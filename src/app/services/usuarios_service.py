# src/app/services/usuarios_service.py
from typing import List, Optional, Tuple
import sqlite3
import secrets
from datetime import datetime, timedelta

from ..db.connection import ConnectionManager
from ..models import Usuario


def obtener_usuarios() -> List[Usuario]:
    """
    Devuelve lista de usuarios como objetos Usuario.
    (omitimos la clave en la respuesta por seguridad).
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nombre, apellido, usuario, clave, rol, email, reset_token, reset_token_expiry 
            FROM usuarios ORDER BY id
        """)
        rows = cur.fetchall()
    
    usuarios = []
    for row in rows:
        # Convertir reset_token_expiry de string a datetime si existe
        expiry = None
        if row[8]:
            try:
                expiry = datetime.fromisoformat(row[8])
            except:
                pass
        usuarios.append(Usuario(
            id=row[0],
            nombre=row[1],
            apellido=row[2],
            usuario=row[3],
            clave=row[4],
            rol=row[5],
            email=row[6],
            reset_token=row[7],
            reset_token_expiry=expiry
        ))
    
    return usuarios


def obtener_usuario_por_id(usuario_id: int) -> Optional[Usuario]:
    """
    Devuelve un objeto Usuario o None si no existe.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nombre, apellido, usuario, clave, rol, email, reset_token, reset_token_expiry 
            FROM usuarios WHERE id = ?
        """, (usuario_id,))
        row = cur.fetchone()
    
    if not row:
        return None
    
    expiry = None
    if row[8]:
        try:
            expiry = datetime.fromisoformat(row[8])
        except:
            pass
    
    return Usuario(
        id=row[0],
        nombre=row[1],
        apellido=row[2],
        usuario=row[3],
        clave=row[4],
        rol=row[5],
        email=row[6],
        reset_token=row[7],
        reset_token_expiry=expiry
    )


def obtener_usuario_por_username(username: str) -> Optional[Usuario]:
    """
    Devuelve un objeto Usuario por nombre de usuario o None si no existe.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nombre, apellido, usuario, clave, rol, email, reset_token, reset_token_expiry 
            FROM usuarios WHERE usuario = ?
        """, (username,))
        row = cur.fetchone()
    
    if not row:
        return None
    
    expiry = None
    if row[8]:
        try:
            expiry = datetime.fromisoformat(row[8])
        except:
            pass
    
    return Usuario(
        id=row[0],
        nombre=row[1],
        apellido=row[2],
        usuario=row[3],
        clave=row[4],
        rol=row[5],
        email=row[6],
        reset_token=row[7],
        reset_token_expiry=expiry
    )


def obtener_usuario_por_email(email: str) -> Optional[Usuario]:
    """
    Devuelve un objeto Usuario por email o None si no existe.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nombre, apellido, usuario, clave, rol, email, reset_token, reset_token_expiry 
            FROM usuarios WHERE email = ?
        """, (email,))
        row = cur.fetchone()
    
    if not row:
        return None
    
    expiry = None
    if row[8]:
        try:
            expiry = datetime.fromisoformat(row[8])
        except:
            pass
    
    return Usuario(
        id=row[0],
        nombre=row[1],
        apellido=row[2],
        usuario=row[3],
        clave=row[4],
        rol=row[5],
        email=row[6],
        reset_token=row[7],
        reset_token_expiry=expiry
    )


def registrar_usuario(nombre: str, apellido: str, usuario: str, clave: str, rol: str, email: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Registra un usuario nuevo.
    Devuelve (ok, mensaje_error, usuario_id).
    """
    try:
        # Validar email si se proporciona
        if email and not Usuario.validar_email(email):
            return False, "El formato del email no es válido", None
        
        # Hashear la contraseña
        clave_hash = Usuario.hash_password(clave)
        
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
            if cur.fetchone()[0] > 0:
                return False, "El nombre de usuario ya existe", None
            
            # Verificar que el email no esté en uso si se proporciona
            if email:
                cur.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", (email,))
                if cur.fetchone()[0] > 0:
                    return False, "El email ya está en uso", None
            
            cur.execute(
                "INSERT INTO usuarios (nombre, apellido, usuario, clave, rol, email) VALUES (?, ?, ?, ?, ?, ?)",
                (nombre, apellido, usuario, clave_hash, rol, email)
            )
            return True, None, cur.lastrowid
    except sqlite3.IntegrityError as e:
        return False, str(e), None
    except Exception as e:
        return False, str(e), None


def actualizar_usuario(usuario_id: int, nombre: str, apellido: str, usuario: str, clave: Optional[str], rol: str, email: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Actualiza un usuario. Si `clave` es None o cadena vacía, no la modifica.
    Devuelve (ok, mensaje_error).
    """
    try:
        # Validar email si se proporciona
        if email and not Usuario.validar_email(email):
            return False, "El formato del email no es válido"
        
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ? AND id != ?", (usuario, usuario_id))
            if cur.fetchone()[0] > 0:
                return False, "El nombre de usuario ya está en uso por otro usuario"
            
            # Verificar que el email no esté en uso por otro usuario
            if email:
                cur.execute("SELECT COUNT(*) FROM usuarios WHERE email = ? AND id != ?", (email, usuario_id))
                if cur.fetchone()[0] > 0:
                    return False, "El email ya está en uso por otro usuario"
            
            if clave:
                # Hashear la nueva contraseña
                clave_hash = Usuario.hash_password(clave)
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, apellido = ?, usuario = ?, clave = ?, rol = ?, email = ? WHERE id = ?",
                    (nombre, apellido, usuario, clave_hash, rol, email, usuario_id)
                )
            else:
                cur.execute(
                    "UPDATE usuarios SET nombre = ?, apellido = ?, usuario = ?, rol = ?, email = ? WHERE id = ?",
                    (nombre, apellido, usuario, rol, email, usuario_id)
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


def validar_credenciales(usuario: str, clave: str) -> Optional[Usuario]:
    """
    Valida las credenciales de un usuario y devuelve el objeto Usuario si son correctas.
    """
    user = obtener_usuario_por_username(usuario)
    if not user:
        return None
    
    # Verificar la contraseña
    if Usuario.verify_password(clave, user.clave):
        return user
    
    return None


def generar_token_recuperacion(email: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Genera un token de recuperación para el email especificado.
    Devuelve (ok, mensaje_error, token).
    """
    try:
        user = obtener_usuario_por_email(email)
        if not user:
            return False, "No existe un usuario con ese email", None
        
        # Generar token aleatorio
        token = secrets.token_urlsafe(32)
        
        # El token expira en 1 hora
        expiry = datetime.now() + timedelta(hours=1)
        
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE usuarios SET reset_token = ?, reset_token_expiry = ? WHERE id = ?",
                (token, expiry.isoformat(), user.id)
            )
        
        return True, None, token
    except Exception as e:
        return False, str(e), None


def validar_token_recuperacion(token: str) -> Tuple[bool, Optional[str], Optional[Usuario]]:
    """
    Valida un token de recuperación.
    Devuelve (ok, mensaje_error, usuario).
    """
    try:
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nombre, apellido, usuario, clave, rol, email, reset_token, reset_token_expiry 
                FROM usuarios WHERE reset_token = ?
            """, (token,))
            row = cur.fetchone()
        
        if not row:
            return False, "Token inválido", None
        
        # Verificar expiración
        if row[8]:
            try:
                expiry = datetime.fromisoformat(row[8])
                if datetime.now() > expiry:
                    return False, "El token ha expirado", None
            except:
                return False, "Token inválido", None
        else:
            return False, "Token inválido", None
        
        user = Usuario(
            id=row[0],
            nombre=row[1],
            apellido=row[2],
            usuario=row[3],
            clave=row[4],
            rol=row[5],
            email=row[6],
            reset_token=row[7],
            reset_token_expiry=expiry
        )
        
        return True, None, user
    except Exception as e:
        return False, str(e), None


def restablecer_contrasena(token: str, nueva_clave: str) -> Tuple[bool, Optional[str]]:
    """
    Restablece la contraseña de un usuario usando un token de recuperación.
    Devuelve (ok, mensaje_error).
    """
    try:
        # Validar el token
        ok, err, user = validar_token_recuperacion(token)
        if not ok:
            return False, err
        
        # Hashear la nueva contraseña
        clave_hash = Usuario.hash_password(nueva_clave)
        
        # Actualizar la contraseña y limpiar el token
        with ConnectionManager() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE usuarios SET clave = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?",
                (clave_hash, user.id)
            )
        
        return True, None
    except Exception as e:
        return False, str(e)
