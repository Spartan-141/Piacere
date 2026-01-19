"""
Script de prueba para verificar que todos los modelos funcionan correctamente
"""
import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from datetime import datetime, date

# Importar todos los modelos
from app.models import (
    Usuario, Seccion, Mesa, MenuSection, MenuItem, MenuItemVariant,
    Orden, OrdenDetalle, Factura, TasaCambio, Producto
)


def test_modelos():
    """Prueba básica de todos los modelos"""
    
    print("🧪 Probando modelos...\n")
    
    # 1. Usuario
    print("✅ Usuario")
    usuario = Usuario(
        id=1,
        nombre="Juan",
        apellido="Pérez",
        usuario="juan",
        clave="123",
        rol="mesero"
    )
    print(f"   {usuario.get_nombre_completo()}")
    print(f"   Es admin: {usuario.es_admin()}")
    print(f"   Puede tomar órdenes: {usuario.puede_tomar_ordenes()}")
    
    # 2. Sección
    print("\n✅ Seccion")
    seccion = Seccion(id=1, nombre="Principal")
    print(f"   {seccion}")
    
    # 3. Mesa
    print("\n✅ Mesa")
    mesa = Mesa(id=1, numero=5, estado="libre", seccion_id=1)
    print(f"   {mesa}")
    print(f"   Disponible: {mesa.esta_disponible()}")
    mesa.ocupar()
    print(f"   Después de ocupar: {mesa.estado}")
    
    # 4. MenuSection
    print("\n✅ MenuSection")
    menu_section = MenuSection(
        id=1,
        nombre="Pizzas",
        descripcion="Pizzas artesanales",
        position=0,
        active=True
    )
    print(f"   {menu_section}")
    print(f"   Activa: {menu_section.esta_activa()}")
    
    # 5. MenuItem
    print("\n✅ MenuItem")
    menu_item = MenuItem(
        id=1,
        section_id=1,
        nombre="Margarita",
        descripcion="Queso y albahaca",
        precio=8.50,
        disponible=True,
        position=0
    )
    print(f"   {menu_item}")
    print(f"   Precio: {menu_item.get_precio_formateado()}")
    
    # 6. MenuItemVariant
    print("\n✅ MenuItemVariant")
    variant = MenuItemVariant(
        id=1,
        menu_item_id=1,
        clave="grande",
        nombre="Grande",
        precio=12.00,
        sku=None,
        position=0,
        active=True
    )
    print(f"   {variant}")
    
    # 7. TasaCambio
    print("\n✅ TasaCambio")
    tasa = TasaCambio(id=1, fecha=date.today(), tasa=36.50)
    print(f"   {tasa}")
    print(f"   $10 = Bs. {tasa.convertir_a_bolivares(10):.2f}")
    
    # 8. Producto
    print("\n✅ Producto")
    producto = Producto(
        id=1,
        nombre="Queso Mozzarella",
        descripcion="Queso para pizzas",
        stock=50,
        precio=5.00
    )
    print(f"   {producto}")
    print(f"   Tiene stock: {producto.tiene_stock(10)}")
    producto.reducir_stock(5)
    print(f"   Después de reducir 5: Stock = {producto.stock}")
    
    # 9. Orden
    print("\n✅ Orden")
    orden = Orden(
        id=1,
        mesa_id=1,
        cliente_nombre="Cliente Test",
        estado="abierta",
        total=25.50,
        fecha=datetime.now()
    )
    print(f"   {orden}")
    print(f"   Total: {orden.get_total_formateado()}")
    print(f"   Está abierta: {orden.esta_abierta()}")
    
    # 10. OrdenDetalle
    print("\n✅ OrdenDetalle")
    detalle = OrdenDetalle(
        id=1,
        orden_id=1,
        menu_item_id=1,
        variant_id=None,
        cantidad=2,
        precio=8.50,
        precio_unitario=8.50,
        subtotal=17.00
    )
    print(f"   {detalle}")
    print(f"   Subtotal: {detalle.get_subtotal_formateado()}")
    
    # 11. Factura
    print("\n✅ Factura")
    factura = Factura(
        id=1,
        orden_id=1,
        numero_factura="001",
        fecha=datetime.now(),
        cliente_nombre="Cliente Test",
        total=25.50
    )
    print(f"   {factura}")
    print(f"   Número: {factura.get_numero_formateado()}")
    
    print("\n\n🎉 ¡Todos los modelos funcionan correctamente!")


if __name__ == "__main__":
    test_modelos()
