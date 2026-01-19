from typing import List, Optional, Tuple
from ..db.connection import crear_conexion, ConnectionManager
from ..models import Mesa, Seccion


def obtener_mesas() -> List[Mesa]:
    """
    Retorna lista de objetos Mesa.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.id, m.numero, m.estado, m.seccion_id
            FROM mesas m
            ORDER BY m.numero
        """
        )
        rows = cur.fetchall()

    return [Mesa(*row) for row in rows]


def obtener_mesa_por_id(mesa_id: int) -> Optional[Mesa]:
    """
    Retorna un objeto Mesa o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, numero, estado, seccion_id
            FROM mesas
            WHERE id = ?
        """,
            (mesa_id,),
        )
        row = cur.fetchone()

    return Mesa(*row) if row else None


def obtener_mesa_por_numero(numero: str) -> Optional[Mesa]:
    """
    Retorna un objeto Mesa por número/nombre o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, numero, estado, seccion_id
            FROM mesas
            WHERE numero = ?
        """,
            (numero,),
        )
        row = cur.fetchone()

    return Mesa(*row) if row else None


def obtener_inicial_seccion(seccion_id: int) -> str:
    """
    Obtiene la inicial (primera letra en mayúscula) del nombre de la sección.
    """
    seccion = obtener_seccion_por_id(seccion_id)
    if seccion and seccion.nombre:
        return seccion.nombre[0].upper()
    return "M"  # Default si no se encuentra la sección


def obtener_siguiente_numero_mesa(seccion_id: int) -> int:
    """
    Calcula el siguiente número disponible para una sección específica.
    Busca el número más alto usado en esa sección y devuelve el siguiente.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        # Obtener todas las mesas de esta sección
        cur.execute(
            """
            SELECT numero FROM mesas WHERE seccion_id = ?
        """,
            (seccion_id,),
        )
        numeros_existentes = cur.fetchall()

    if not numeros_existentes:
        return 1

    # Extraer los números de los nombres (ej: "Mesa P3" -> 3)
    numeros = []
    for (nombre,) in numeros_existentes:
        try:
            # Formato esperado: "Mesa [Inicial][Numero]"
            # Extraer el número al final
            partes = nombre.split()
            if len(partes) >= 2:
                # El último elemento debería ser algo como "P3", "T2", etc.
                codigo = partes[-1]
                # Extraer solo los dígitos
                numero_str = "".join(filter(str.isdigit, codigo))
                if numero_str:
                    numeros.append(int(numero_str))
        except (ValueError, IndexError):
            continue

    return max(numeros) + 1 if numeros else 1


def generar_nombre_mesa(seccion_id: int) -> str:
    """
    Genera el nombre completo de una mesa en formato "Mesa [Inicial][Número]".
    Ejemplo: "Mesa P1", "Mesa T2", etc.
    """
    inicial = obtener_inicial_seccion(seccion_id)
    numero = obtener_siguiente_numero_mesa(seccion_id)
    return f"Mesa {inicial}{numero}"


def crear_mesa(seccion_id: int) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Crea una mesa con nombre auto-generado. Retorna (ok, error, mesa_id).
    """
    with ConnectionManager() as conn:
        try:
            # Generar nombre automáticamente
            numero = generar_nombre_mesa(seccion_id)

            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM mesas WHERE numero = ?", (numero,))
            if cur.fetchone()[0] > 0:
                return False, "Ya existe una mesa con ese nombre", None
            cur.execute(
                "INSERT INTO mesas (numero, seccion_id, estado) VALUES (?, ?, ?)",
                (numero, seccion_id, "libre"),
            )
            return True, None, cur.lastrowid
        except Exception as e:
            conn.rollback()
            return False, str(e), None


def actualizar_mesa(
    mesa_id: int, numero: str, estado: str, seccion_id: int
) -> Tuple[bool, Optional[str]]:
    """
    Actualiza una mesa. Retorna (ok, error).
    """
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM mesas WHERE numero = ? AND id != ?",
                (numero, mesa_id),
            )
            if cur.fetchone()[0] > 0:
                return False, "Ya existe otra mesa con ese nombre"
            cur.execute(
                "UPDATE mesas SET numero = ?, estado = ?, seccion_id = ? WHERE id = ?",
                (numero, estado, seccion_id, mesa_id),
            )
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)


def eliminar_mesa(mesa_id: int) -> Tuple[bool, Optional[str]]:
    """
    Intenta eliminar la mesa. Retorna (ok, error).
    """
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            # comprobar órdenes abiertas
            try:
                cur.execute(
                    "SELECT COUNT(*) FROM ordenes WHERE mesa_id = ? AND estado = 'abierta'",
                    (mesa_id,),
                )
                if cur.fetchone()[0] > 0:
                    return False, "No se puede eliminar: la mesa tiene órdenes abiertas"
            except Exception:
                pass
            cur.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)


def cambiar_estado_mesa(mesa_id: int, nuevo_estado: str) -> Tuple[bool, Optional[str]]:
    """
    Cambia el estado de una mesa. Retorna (ok, error).
    """
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE mesas SET estado = ? WHERE id = ?", (nuevo_estado, mesa_id)
            )
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)


# --- Secciones ---


def obtener_secciones() -> List[Seccion]:
    """
    Devuelve lista de objetos Seccion.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM secciones ORDER BY nombre")
        rows = cur.fetchall()

    return [Seccion(*row) for row in rows]


def obtener_seccion_por_id(seccion_id: int) -> Optional[Seccion]:
    """
    Retorna un objeto Seccion o None.
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM secciones WHERE id = ?", (seccion_id,))
        row = cur.fetchone()

    return Seccion(*row) if row else None


def crear_seccion(nombre: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Crea una sección. Retorna (ok, error, seccion_id).
    """
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO secciones (nombre) VALUES (?)", (nombre,))
            conn.commit()
            return True, None, cur.lastrowid
        except Exception as e:
            conn.rollback()
            return False, str(e), None


def eliminar_seccion(seccion_id: int) -> Tuple[bool, Optional[str]]:
    """
    Elimina una sección si no tiene mesas asociadas.
    Retorna (ok, error).
    """
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            # comprobar mesas asociadas
            cur.execute(
                "SELECT COUNT(*) FROM mesas WHERE seccion_id = ?", (seccion_id,)
            )
            if cur.fetchone()[0] > 0:
                return False, "No se puede eliminar: la sección tiene mesas asociadas"

            cur.execute("DELETE FROM secciones WHERE id = ?", (seccion_id,))
            conn.commit()
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)
