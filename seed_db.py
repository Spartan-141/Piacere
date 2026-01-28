import sys
import os
import random
from datetime import datetime, timedelta

# Añadir 'src' al path para poder importar los módulos del app
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from app.db.connection import ConnectionManager
except ImportError as e:
    print(f"Error: No se pudo importar ConnectionManager. Asegúrese de ejecutar el script desde la raíz del proyecto. {e}")
    sys.exit(1)

def seed():
    print("Iniciando generación de datos de prueba...")
    
    with ConnectionManager() as conn:
        cur = conn.cursor()
        
        # 1. Limpiar datos existentes (Opcional, pero recomendado para un seed limpio)
        print("Limpiando tablas...")
        cur.execute("DELETE FROM facturas")
        cur.execute("DELETE FROM orden_detalles")
        cur.execute("DELETE FROM ordenes")
        cur.execute("DELETE FROM menu_items")
        cur.execute("DELETE FROM menu_sections")
        cur.execute("DELETE FROM mesas")
        cur.execute("DELETE FROM secciones")
        cur.execute("DELETE FROM usuarios WHERE usuario NOT IN ('admin', 'mesero')")
        
        # 2. Usuarios
        print("Creando usuarios...")
        usuarios = [
            ("Juan", "Pérez", "juanp", "1234", "mesero", "juan@example.com"),
            ("María", "García", "mariag", "1234", "mesero", "maria@example.com"),
            ("Carlos", "Rodríguez", "carlosr", "1234", "admin", "carlos@example.com"),
            ("Ana", "Martínez", "anam", "1234", "mesero", "ana@example.com"),
        ]
        cur.executemany(
            "INSERT INTO usuarios (nombre, apellido, usuario, clave, rol, email) VALUES (?, ?, ?, ?, ?, ?)",
            usuarios
        )
        
        # 3. Secciones y Mesas
        print("Creando secciones y mesas...")
        areas = ["Salón Principal", "Terraza", "VIP", "Bar"]
        for area in areas:
            cur.execute("INSERT INTO secciones (nombre) VALUES (?)", (area,))
            seccion_id = cur.lastrowid
            
            inicial = area[0].upper()
            num_mesas = random.randint(5, 10)
            for i in range(1, num_mesas + 1):
                cur.execute(
                    "INSERT INTO mesas (numero, seccion_id, estado) VALUES (?, ?, ?)",
                    (f"Mesa {inicial}{i}", seccion_id, "libre")
                )
        
        # 4. Menú (Secciones e Items)
        print("Creando menú...")
        menu_data = {
            "Pizzas": [
                ("Margarita", 8.5, "Tomate, mozzarella, albahaca"),
                ("Pepperoni", 10.0, "Mozzarella y abundante pepperoni"),
                ("Hawaiana", 9.5, "Jamón y piña"),
                ("Cuatro Quesos", 12.0, "Mozzarella, parmesano, gorgonzola, provolone"),
                ("Vegetariana", 11.0, "Pimientos, cebolla, aceitunas, champiñones"),
                ("Carbonara", 11.5, "Nata, bacon, cebolla"),
                ("BBQ Chicken", 13.0, "Pollo, salsa BBQ, cebolla morada")
            ],
            "Pastas": [
                ("Lasagna", 12.0, "Lasagna de carne al horno"),
                ("Fetuccini Alfredo", 11.0, "Salsa blanca cremosa con pollo"),
                ("Espagueti Boloñesa", 10.5, "Salsa de tomate con carne"),
                ("Penne Arrabbiata", 9.5, "Salsa de tomate picante")
            ],
            "Bebidas": [
                ("Coca Cola 350ml", 1.5, "Refresco de cola"),
                ("Fanta Naranja", 1.5, "Refresco de naranja"),
                ("Agua Mineral", 1.0, "Botella 500ml"),
                ("Cerveza Nacional", 2.0, "Botella 330ml"),
                ("Jugo Natural", 2.5, "Naranja, Fresa o Piña")
            ],
            "Postres": [
                ("Tiramisú", 5.0, "Clásico postre italiano"),
                ("Cheesecake", 4.5, "Tarta de queso con frutos rojos"),
                ("Brownie con Helado", 4.0, "Brownie tibio con una bola de helado"),
                ("Copa de Helado", 3.0, "3 bolas de helado variado")
            ]
        }
        
        item_ids = []
        for section_name, items in menu_data.items():
            cur.execute("INSERT INTO menu_sections (nombre, active) VALUES (?, 1)", (section_name,))
            sec_id = cur.lastrowid
            for name, price, desc in items:
                cur.execute(
                    "INSERT INTO menu_items (section_id, nombre, precio, descripcion, disponible) VALUES (?, ?, ?, ?, 1)",
                    (sec_id, name, price, desc)
                )
                item_ids.append((cur.lastrowid, price))
        
        # 5. Órdenes y Facturas (Histórico)
        print("Generando histórico de facturas (esto puede tardar un poco)...")
        clientes = ["Finalizado", "Cliente Ocasional", "Empresa X", "Familia López", "Pedro S.", "María C.", "Grup de Amigos"]
        formas_pago = ["Efectivo", "Tarjeta", "Transferencia", "Pago Móvil"]
        tasa_usd_ves = 50.0 # Tasa simulada
        
        start_date = datetime.now() - timedelta(days=180) # 6 meses atrás
        
        total_facturas = 600
        for i in range(total_facturas):
            # Fecha aleatoria en los últimos 180 días
            days_offset = random.randint(0, 180)
            hours_offset = random.randint(8, 22)
            minutes_offset = random.randint(0, 59)
            fecha_orden = start_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
            fecha_str = fecha_orden.strftime("%Y-%m-%d %H:%M:%S")
            
            # Datos de orden
            cliente = random.choice(clientes)
            cur.execute(
                "INSERT INTO ordenes (mesa_id, cliente_nombre, estado, fecha, cerrado_en) VALUES (?, ?, ?, ?, ?)",
                (random.randint(1, 10), cliente, "finalizada", fecha_str, fecha_str)
            )
            orden_id = cur.lastrowid
            
            # Detalles de la orden (2 a 5 items)
            num_items = random.randint(2, 5)
            subtotal_orden = 0
            for _ in range(num_items):
                item_id, precio = random.choice(item_ids)
                cantidad = random.randint(1, 3)
                subtotal = precio * cantidad
                cur.execute(
                    "INSERT INTO orden_detalles (orden_id, menu_item_id, cantidad, precio, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (orden_id, item_id, cantidad, precio, subtotal)
                )
                subtotal_orden += subtotal
            
            # Actualizar total de la orden
            cur.execute("UPDATE ordenes SET total = ? WHERE id = ?", (subtotal_orden, orden_id))
            
            # Crear factura
            num_factura = f"FACT-{2024}-{i+1:05d}"
            forma_pago = random.choice(formas_pago)
            total_ves = subtotal_orden * tasa_usd_ves
            
            cur.execute(
                """INSERT INTO facturas (orden_id, numero_factura, fecha, cliente_nombre, forma_pago, total, total_ves) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (orden_id, num_factura, fecha_str, cliente, forma_pago, subtotal_orden, total_ves)
            )
        
        conn.commit()
    
    print(f"¡Éxito! Se han creado {total_facturas} facturas de prueba y datos maestros.")

if __name__ == "__main__":
    seed()
