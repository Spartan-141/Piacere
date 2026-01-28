# src/app/db/init_db.py
from .connection import crear_conexion
from sqlite3 import Error
import logging

logger = logging.getLogger(__name__)


def migrar_usuarios_agregar_email_y_recovery():
    """
    Migra la tabla usuarios para agregar campos email, reset_token y reset_token_expiry
    """
    conn = crear_conexion()
    if not conn:
        logger.error("No se pudo conectar para migrar usuarios")
        return False

    try:
        cur = conn.cursor()

        # Verificar si la tabla usuarios existe y necesita migración
        cur.execute("PRAGMA table_info(usuarios)")
        columns = {row[1]: row[2] for row in cur.fetchall()}

        needs_migration = False
        if "email" not in columns:
            logger.info("Agregando campo email a tabla usuarios...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN email TEXT")
            needs_migration = True

        if "reset_token" not in columns:
            logger.info("Agregando campo reset_token a tabla usuarios...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN reset_token TEXT")
            needs_migration = True

        if "reset_token_expiry" not in columns:
            logger.info("Agregando campo reset_token_expiry a tabla usuarios...")
            cur.execute("ALTER TABLE usuarios ADD COLUMN reset_token_expiry TIMESTAMP")
            needs_migration = True

        if needs_migration:
            conn.commit()
            logger.info("Migración de usuarios completada exitosamente")
        else:
            logger.info("La tabla usuarios ya tiene todos los campos necesarios")

        return True

    except Error as e:
        logger.exception(f"Error durante la migración de usuarios: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def migrar_hashear_passwords_existentes():
    """
    Migra las contraseñas en texto plano a hash bcrypt/SHA256.
    Detecta contraseñas que no son hash y las convierte.
    """
    conn = crear_conexion()
    if not conn:
        logger.error("No se pudo conectar para migrar contraseñas")
        return False

    try:
        from ..models import Usuario
        cur = conn.cursor()

        # Obtener todos los usuarios
        cur.execute("SELECT id, clave FROM usuarios")
        usuarios = cur.fetchall()

        passwords_migrated = 0
        for user_id, clave in usuarios:
            # Verificar si la contraseña ya está hasheada
            # Bcrypt empieza con $2
            # SHA256 tiene exactamente 64 caracteres hexadecimales
            is_bcrypt = clave.startswith('$2')
            is_sha256 = len(clave) == 64 and all(c in '0123456789abcdef' for c in clave.lower())
            
            if not is_bcrypt and not is_sha256:
                # Es texto plano, convertir a hash
                logger.info(f"Hasheando contraseña para usuario ID {user_id}...")
                clave_hash = Usuario.hash_password(clave)
                cur.execute("UPDATE usuarios SET clave = ? WHERE id = ?", (clave_hash, user_id))
                passwords_migrated += 1

        if passwords_migrated > 0:
            conn.commit()
            logger.info(f"Migración de contraseñas completada: {passwords_migrated} contraseñas hasheadas")
        else:
            logger.info("Todas las contraseñas ya están hasheadas correctamente")

        return True

    except Error as e:
        logger.exception(f"Error durante la migración de contraseñas: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def migrar_mesas_a_texto():
    """
    Migra el campo numero de INTEGER a TEXT y convierte los datos existentes
    al nuevo formato (ej: numero=1 en seccion 'Principal' -> 'Mesa P1')
    """
    conn = crear_conexion()
    if not conn:
        logger.error("No se pudo conectar para migrar mesas")
        return False

    try:
        cur = conn.cursor()

        # Verificar si la tabla mesas existe y tiene el formato antiguo
        cur.execute("PRAGMA table_info(mesas)")
        columns = {row[1]: row[2] for row in cur.fetchall()}

        if "numero" in columns and columns["numero"] == "INTEGER":
            logger.info("Migrando tabla mesas de INTEGER a TEXT...")

            # Obtener todas las mesas actuales con sus secciones
            cur.execute(
                """
                SELECT m.id, m.numero, m.estado, m.seccion_id, s.nombre
                FROM mesas m
                LEFT JOIN secciones s ON m.seccion_id = s.id
            """
            )
            mesas_actuales = cur.fetchall()

            # Crear tabla temporal con el nuevo esquema
            cur.execute(
                """
                CREATE TABLE mesas_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'libre',
                    seccion_id INTEGER NOT NULL,
                    FOREIGN KEY (seccion_id) REFERENCES secciones (id)
                )
            """
            )

            # Migrar datos al nuevo formato
            for mesa_id, numero, estado, seccion_id, seccion_nombre in mesas_actuales:
                # Obtener inicial de la sección
                inicial = seccion_nombre[0].upper() if seccion_nombre else "M"
                nuevo_nombre = f"Mesa {inicial}{numero}"

                cur.execute(
                    """
                    INSERT INTO mesas_new (id, numero, estado, seccion_id)
                    VALUES (?, ?, ?, ?)
                """,
                    (mesa_id, nuevo_nombre, estado, seccion_id),
                )

            # Eliminar tabla antigua y renombrar la nueva
            cur.execute("DROP TABLE mesas")
            cur.execute("ALTER TABLE mesas_new RENAME TO mesas")

            conn.commit()
            logger.info("Migración de mesas completada exitosamente")
            return True
        else:
            logger.info("La tabla mesas ya tiene el formato correcto")
            return True

    except Error as e:
        logger.exception(f"Error durante la migración: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def migrar_orden_detalles_agregar_estado_cocina():
    """
    Migra la tabla orden_detalles para agregar el campo estado_cocina
    """
    conn = crear_conexion()
    if not conn:
        logger.error("No se pudo conectar para migrar orden_detalles")
        return False

    try:
        cur = conn.cursor()

        # Verificar si la columna ya existe
        cur.execute("PRAGMA table_info(orden_detalles)")
        columns = {row[1]: row[2] for row in cur.fetchall()}

        if "estado_cocina" not in columns:
            logger.info("Agregando campo estado_cocina a tabla orden_detalles...")
            cur.execute("ALTER TABLE orden_detalles ADD COLUMN estado_cocina TEXT DEFAULT 'pendiente'")
            conn.commit()
            logger.info("Migración de orden_detalles completada exitosamente")
        else:
            logger.info("La tabla orden_detalles ya tiene el campo estado_cocina")

        return True

    except Error as e:
        logger.exception(f"Error durante la migración de orden_detalles: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def inicializar_base_datos() -> bool:
    """
    Crear tablas, triggers e índices necesarios para la aplicación.
    Devuelve True si la inicialización se completó (o ya estaba aplicada).
    """
    comandos = [
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            rol TEXT NOT NULL,
            email TEXT,
            reset_token TEXT,
            reset_token_expiry TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            estado TEXT NOT NULL DEFAULT 'libre',
            seccion_id INTEGER NOT NULL,
            FOREIGN KEY (seccion_id) REFERENCES secciones (id)
        )""",
        """CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER NOT NULL,
            cliente_nombre TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'abierta',
            total REAL DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP,
            cerrado_en TIMESTAMP,
            FOREIGN KEY (mesa_id) REFERENCES mesas (id)
        )""",
        """CREATE TABLE IF NOT EXISTS orden_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            menu_item_id INTEGER DEFAULT NULL,
            variant_id INTEGER DEFAULT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            precio_unitario REAL DEFAULT NULL,
            subtotal REAL NOT NULL,
            estado_cocina TEXT DEFAULT 'pendiente',
            FOREIGN KEY (orden_id) REFERENCES ordenes (id)
        )""",
        """CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            numero_factura TEXT UNIQUE NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_nombre TEXT NOT NULL,
            forma_pago TEXT NOT NULL,
            total REAL NOT NULL,
            total_ves REAL NOT NULL,
            FOREIGN KEY (orden_id) REFERENCES ordenes (id)
        )""",
        """CREATE TABLE IF NOT EXISTS tasas_cambio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE NOT NULL UNIQUE,
            tasa REAL NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS menu_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT DEFAULT NULL,
            position INTEGER DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        )""",
        """CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT DEFAULT NULL,
            precio REAL NOT NULL DEFAULT 0.0,
            disponible INTEGER NOT NULL DEFAULT 1,
            position INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (section_id) REFERENCES menu_sections(id) ON DELETE RESTRICT
        )""",
        """CREATE TABLE IF NOT EXISTS menu_item_variant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_item_id INTEGER NOT NULL,
            clave TEXT NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            sku TEXT DEFAULT NULL,
            position INTEGER DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            UNIQUE(menu_item_id, clave),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT DEFAULT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            precio REAL NOT NULL DEFAULT 0.0
            )""",
    ]

    actualizaciones = [
        # Trigger para prevenir stock negativo en productos (legacy)
        "CREATE TRIGGER IF NOT EXISTS prevent_negative_stock "
        "BEFORE UPDATE ON productos "
        "FOR EACH ROW "
        "WHEN NEW.stock < 0 "
        "BEGIN "
        "   SELECT RAISE(ABORT, 'Stock no puede ser negativo'); "
        "END;",
        # Índice para evitar más de una orden abierta por mesa
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_mesa_orden_abierta "
        "ON ordenes(mesa_id) WHERE estado = 'abierta';",
        # Índices para orden_detalles
        "CREATE INDEX IF NOT EXISTS idx_orden_detalles_menu_item ON orden_detalles(menu_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_orden_detalles_orden ON orden_detalles(orden_id);",
        "CREATE INDEX IF NOT EXISTS idx_orden_detalles_estado_cocina ON orden_detalles(estado_cocina);",
        # Índices para menú
        "CREATE INDEX IF NOT EXISTS idx_menu_items_section ON menu_items(section_id);",
        "CREATE INDEX IF NOT EXISTS idx_menu_sections_position ON menu_sections(position);",
        "CREATE INDEX IF NOT EXISTS idx_variant_menu_item ON menu_item_variant(menu_item_id);",
    ]

    conn = crear_conexion()
    if not conn:
        logger.error("Inicialización abortada: no se pudo obtener conexión")
        return False

    try:
        cur = conn.cursor()

        # Asegurar que SQLite respete FKs
        try:
            cur.execute("PRAGMA foreign_keys = ON;")
        except Exception:
            pass

        # Ejecutar creación de tablas
        for sql in comandos:
            try:
                cur.execute(sql)
            except Error:
                logger.exception("Error al ejecutar comando de creación: %s", sql)

        # Ejecutar actualizaciones (triggers, índices)
        for sql in actualizaciones:
            try:
                cur.execute(sql)
            except Error:
                logger.debug("Actualización omitida o ya aplicada: %s", sql)

        conn.commit()

        # Seed inicial (solo si la tabla usuarios está vacía)
        try:
            cur.execute("SELECT COUNT(*) FROM usuarios")
            if cur.fetchone()[0] == 0:
                # usuario admin por defecto (cambiar contraseña en primer uso)
                cur.execute(
                    "INSERT INTO usuarios (nombre, apellido, usuario, clave, rol) VALUES (?, ?, ?, ?, ?)",
                    ("Administrador", "", "admin", "admin", "admin"),
                )

                # Crear secciones iniciales de mesas
                cur.execute("INSERT INTO secciones (nombre) VALUES (?)", ("Principal",))
                cur.execute("INSERT INTO secciones (nombre) VALUES (?)", ("Terraza",))

                cur.execute("SELECT id FROM secciones WHERE nombre = ?", ("Principal",))
                principal_id = cur.fetchone()[0]
                cur.execute("SELECT id FROM secciones WHERE nombre = ?", ("Terraza",))
                terraza_id = cur.fetchone()[0]

                # Crear mesas asociadas con nuevo formato de nombres
                for i in range(1, 6):
                    cur.execute(
                        "INSERT INTO mesas (numero, seccion_id) VALUES (?, ?)",
                        (f"Mesa P{i}", principal_id),
                    )
                for i in range(1, 6):
                    cur.execute(
                        "INSERT INTO mesas (numero, seccion_id) VALUES (?, ?)",
                        (f"Mesa T{i}", terraza_id),
                    )

                # Crear secciones del menú y algunos items de ejemplo
                cur.execute(
                    "INSERT OR IGNORE INTO menu_sections (nombre, descripcion, position, active) VALUES (?, ?, ?, ?)",
                    ("Pizzas", "Pizzas artesanales", 0, 1),
                )
                cur.execute(
                    "INSERT OR IGNORE INTO menu_sections (nombre, descripcion, position, active) VALUES (?, ?, ?, ?)",
                    ("Bebidas", None, 1, 1),
                )
                cur.execute(
                    "INSERT OR IGNORE INTO menu_sections (nombre, descripcion, position, active) VALUES (?, ?, ?, ?)",
                    ("Postres", None, 2, 1),
                )

                # Obtener ids de secciones del menú
                cur.execute(
                    "SELECT id FROM menu_sections WHERE nombre = ?", ("Pizzas",)
                )
                row = cur.fetchone()
                pizzas_section = row[0] if row else None

                cur.execute(
                    "SELECT id FROM menu_sections WHERE nombre = ?", ("Bebidas",)
                )
                row = cur.fetchone()
                bebidas_section = row[0] if row else None

                cur.execute(
                    "SELECT id FROM menu_sections WHERE nombre = ?", ("Postres",)
                )
                row = cur.fetchone()
                postres_section = row[0] if row else None

                # Insertar items ejemplo (si no existen)
                if pizzas_section:
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            pizzas_section,
                            "Margarita",
                            "Queso, salsa y albahaca",
                            8.50,
                            1,
                            0,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (pizzas_section, "Pepperoni", "Pepperoni extra", 9.50, 1, 1),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            pizzas_section,
                            "Cuatro Quesos",
                            "Mozzarella, gorgonzola, parmesano y provolone",
                            10.50,
                            1,
                            2,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (pizzas_section, "Hawaiana", "Jamón y piña", 9.00, 1, 3),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            pizzas_section,
                            "Vegetariana",
                            "Verduras frescas de temporada",
                            9.50,
                            1,
                            4,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            pizzas_section,
                            "Carnívora",
                            "Carne molida, pepperoni, jamón y salchicha",
                            11.00,
                            1,
                            5,
                        ),
                    )

                if bebidas_section:
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            bebidas_section,
                            "Coca-Cola",
                            "Bebida gaseosa 350ml",
                            1.50,
                            1,
                            0,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (bebidas_section, "Agua Mineral", "Botella 500ml", 1.00, 1, 1),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            bebidas_section,
                            "Jugo Natural",
                            "Jugo de frutas frescas",
                            2.50,
                            1,
                            2,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (bebidas_section, "Cerveza", "Botella 330ml", 2.00, 1, 3),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            bebidas_section,
                            "Vino Tinto",
                            "Copa de vino tinto",
                            3.50,
                            1,
                            4,
                        ),
                    )

                if postres_section:
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            postres_section,
                            "Tiramisú",
                            "Clásico italiano con café y mascarpone",
                            4.50,
                            1,
                            0,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            postres_section,
                            "Helado",
                            "Tres bolas de helado a elección",
                            3.00,
                            1,
                            1,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            postres_section,
                            "Cheesecake",
                            "Tarta de queso con frutos rojos",
                            4.00,
                            1,
                            2,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            postres_section,
                            "Brownie",
                            "Brownie de chocolate con nueces",
                            3.50,
                            1,
                            3,
                        ),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO menu_items (section_id, nombre, descripcion, precio, disponible, position) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            postres_section,
                            "Panna Cotta",
                            "Postre italiano con crema y frutas",
                            4.00,
                            1,
                            4,
                        ),
                    )

                conn.commit()
        except Error:
            logger.exception("Error al insertar datos iniciales")

        # Ejecutar migraciones
        conn.close()
        migrar_mesas_a_texto()
        migrar_usuarios_agregar_email_y_recovery()
        migrar_hashear_passwords_existentes()
        migrar_orden_detalles_agregar_estado_cocina()

        return True
    except Error:
        logger.exception("Error inicializando la base de datos")
        return False
    finally:
        if conn:
            conn.close()

