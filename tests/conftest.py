"""
Configuración global de pytest y fixtures compartidos.
"""
import pytest
import sqlite3
import sys
from pathlib import Path
import datetime

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.models import (
    Usuario, Mesa, Seccion, MenuSection, MenuItem, MenuItemVariant,
    TasaCambio, Producto, Orden, OrdenDetalle, Factura
)


# ==================== Fixtures de Base de Datos ====================

@pytest.fixture
def db_memory():
    """
    Crea una base de datos SQLite en memoria para tests.
    Se destruye automáticamente al finalizar el test.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Crear tablas necesarias
    cursor.executescript("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            disponible INTEGER DEFAULT 1,
            rol TEXT DEFAULT 'mesero'
        );
        
        CREATE TABLE secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        );
        
        CREATE TABLE mesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            estado TEXT DEFAULT 'libre',
            seccion_id INTEGER,
            FOREIGN KEY (seccion_id) REFERENCES secciones(id)
        );
        
        CREATE TABLE menu_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            position INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        );
        
        CREATE TABLE menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            disponible INTEGER DEFAULT 1,
            position INTEGER DEFAULT 0,
            created_at TEXT,
            FOREIGN KEY (section_id) REFERENCES menu_sections(id)
        );
        
        CREATE TABLE menu_item_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            precio_adicional REAL DEFAULT 0.0,
            disponible INTEGER DEFAULT 1,
            FOREIGN KEY (item_id) REFERENCES menu_items(id)
        );
        
        CREATE TABLE tasas_cambio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT UNIQUE NOT NULL,
            tasa REAL NOT NULL
        );
        
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0
        );
        
        CREATE TABLE ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER NOT NULL,
            cliente_nombre TEXT,
            total REAL DEFAULT 0.0,
            estado TEXT DEFAULT 'abierta',
            fecha TEXT,
            FOREIGN KEY (mesa_id) REFERENCES mesas(id)
        );
        
        CREATE TABLE orden_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            variant_id INTEGER,
            FOREIGN KEY (orden_id) REFERENCES ordenes(id),
            FOREIGN KEY (item_id) REFERENCES menu_items(id)
        );
        
        CREATE TABLE facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura TEXT UNIQUE NOT NULL,
            fecha TEXT NOT NULL,
            cliente_nombre TEXT,
            total REAL NOT NULL,
            orden_id INTEGER,
            FOREIGN KEY (orden_id) REFERENCES ordenes(id)
        );
    """)
    
    conn.commit()
    yield conn
    conn.close()


# ==================== Fixtures de Modelos ====================

@pytest.fixture
def usuario_admin():
    """Usuario administrador de prueba."""
    return Usuario(
        id=1,
        nombre="Admin",
        apellido="Test",
        usuario="admin",
        clave="admin123",
        rol="admin"
    )


@pytest.fixture
def usuario_mesero():
    """Usuario mesero de prueba."""
    return Usuario(
        id=2,
        nombre="Mesero",
        apellido="Test",
        usuario="mesero",
        clave="mesero123",
        rol="mesero"
    )


@pytest.fixture
def seccion_principal():
    """Sección de prueba."""
    return Seccion(id=1, nombre="Salón Principal")


@pytest.fixture
def mesa_disponible():
    """Mesa disponible de prueba."""
    return Mesa(
        id=1,
        numero=5,
        estado="libre",
        seccion_id=1
    )


@pytest.fixture
def mesa_ocupada():
    """Mesa ocupada de prueba."""
    return Mesa(
        id=2,
        numero=10,
        estado="ocupada",
        seccion_id=1
    )


@pytest.fixture
def menu_section_entradas():
    """Sección de menú de prueba."""
    return MenuSection(
        id=1,
        nombre="Entradas",
        descripcion="Entradas variadas",
        position=1,
        active=True
    )


@pytest.fixture
def menu_item_ensalada():
    """Item de menú de prueba."""
    return MenuItem(
        id=1,
        section_id=1,
        nombre="Ensalada César",
        descripcion="Ensalada fresca",
        precio=12.50,
        disponible=True,
        position=1,
        created_at=datetime.datetime.now().isoformat()
    )


@pytest.fixture
def tasa_actual():
    """Tasa de cambio actual de prueba."""
    return TasaCambio(
        id=1,
        fecha=datetime.date.today(),
        tasa=42.50
    )


@pytest.fixture
def producto_refresco():
    """Producto de prueba."""
    return Producto(
        id=1,
        nombre="Coca Cola",
        descripcion="Refresco 500ml",
        precio=2.50,
        stock=100
    )


@pytest.fixture
def orden_abierta():
    """Orden abierta de prueba."""
    return Orden(
        id=1,
        mesa_id=1,
        cliente_nombre="Juan Pérez",
        total=0.0,
        estado="abierta",
        fecha=datetime.datetime.now().isoformat()
    )


@pytest.fixture
def factura_ejemplo():
    """Factura de prueba."""
    return Factura(
        id=1,
        numero_factura="FACT-20240115-001",
        fecha=datetime.date.today().isoformat(),
        cliente_nombre="María García",
        total=125.50,
        orden_id=1
    )


# ==================== Helpers ====================

@pytest.fixture
def insertar_datos_prueba(db_memory):
    """
    Inserta datos de prueba en la base de datos.
    Retorna un dict con los IDs insertados.
    """
    cursor = db_memory.cursor()
    
    # Insertar usuario
    cursor.execute(
        "INSERT INTO usuarios (nombre, usuario, clave, rol) VALUES (?, ?, ?, ?)",
        ("Admin", "admin", "admin123", "admin")
    )
    usuario_id = cursor.lastrowid
    
    # Insertar sección
    cursor.execute("INSERT INTO secciones (nombre) VALUES (?)", ("Salón Principal",))
    seccion_id = cursor.lastrowid
    
    # Insertar mesa
    cursor.execute(
        "INSERT INTO mesas (numero, estado, seccion_id) VALUES (?, ?, ?)",
        (5, "libre", seccion_id)
    )
    mesa_id = cursor.lastrowid
    
    # Insertar sección de menú
    cursor.execute(
        "INSERT INTO menu_sections (nombre, descripcion, active) VALUES (?, ?, ?)",
        ("Entradas", "Entradas variadas", 1)
    )
    menu_section_id = cursor.lastrowid
    
    # Insertar item de menú
    cursor.execute(
        "INSERT INTO menu_items (section_id, nombre, precio, disponible) VALUES (?, ?, ?, ?)",
        (menu_section_id, "Ensalada", 12.50, 1)
    )
    menu_item_id = cursor.lastrowid
    
    # Insertar tasa de cambio
    cursor.execute(
        "INSERT INTO tasas_cambio (fecha, tasa) VALUES (?, ?)",
        (datetime.date.today().isoformat(), 42.50)
    )
    
    # Insertar producto
    cursor.execute(
        "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
        ("Coca Cola", 2.50, 100)
    )
    producto_id = cursor.lastrowid
    
    db_memory.commit()
    
    return {
        "usuario_id": usuario_id,
        "seccion_id": seccion_id,
        "mesa_id": mesa_id,
        "menu_section_id": menu_section_id,
        "menu_item_id": menu_item_id,
        "producto_id": producto_id
    }
