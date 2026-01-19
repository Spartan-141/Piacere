"""
Script de prueba para verificar que menu_service.py funciona con modelos
"""
import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from app.services import menu_service
from app.models import MenuSection, MenuItem


def test_menu_service():
    """Prueba el servicio de menú refactorizado"""
    
    print("🧪 Probando menu_service.py refactorizado...\n")
    
    # 1. Listar secciones
    print("✅ Listar secciones")
    secciones = menu_service.listar_secciones()
    print(f"   Encontradas {len(secciones)} secciones")
    
    for seccion in secciones:
        print(f"   • {seccion.nombre} (ID: {seccion.id})")
        print(f"     Tipo: {type(seccion).__name__}")  # Debe ser MenuSection
        print(f"     Activa: {seccion.esta_activa()}")
        
        # Verificar que es un objeto MenuSection
        assert isinstance(seccion, MenuSection), "❌ No es un objeto MenuSection!"
    
    # 2. Obtener items de una sección
    if secciones:
        primera_seccion = secciones[0]
        print(f"\n✅ Listar items de '{primera_seccion.nombre}'")
        items = menu_service.listar_items_por_seccion(primera_seccion.id)
        print(f"   Encontrados {len(items)} items")
        
        for item in items:
            print(f"   • {item.nombre} - {item.get_precio_formateado()}")
            print(f"     Tipo: {type(item).__name__}")  # Debe ser MenuItem
            print(f"     Disponible: {item.esta_disponible()}")
            
            # Verificar que es un objeto MenuItem
            assert isinstance(item, MenuItem), "❌ No es un objeto MenuItem!"
    
    # 3. Buscar items por nombre
    print("\n✅ Buscar items por nombre")
    resultados = menu_service.buscar_items_por_nombre("pizza")
    print(f"   Encontrados {len(resultados)} items con 'pizza'")
    
    for item in resultados:
        print(f"   • {item.nombre}")
        assert isinstance(item, MenuItem), "❌ No es un objeto MenuItem!"
    
    # 4. Obtener una sección por ID
    if secciones:
        print("\n✅ Obtener sección por ID")
        seccion = menu_service.obtener_seccion_por_id(secciones[0].id)
        if seccion:
            print(f"   Sección: {seccion.nombre}")
            print(f"   Tipo: {type(seccion).__name__}")
            assert isinstance(seccion, MenuSection), "❌ No es un objeto MenuSection!"
    
    # 5. Obtener un item por ID
    if secciones:
        items = menu_service.listar_items_por_seccion(secciones[0].id)
        if items:
            print("\n✅ Obtener item por ID")
            item = menu_service.obtener_item_por_id(items[0].id)
            if item:
                print(f"   Item: {item.nombre}")
                print(f"   Precio: {item.get_precio_formateado()}")
                print(f"   Tipo: {type(item).__name__}")
                assert isinstance(item, MenuItem), "❌ No es un objeto MenuItem!"
    
    print("\n\n🎉 ¡Todas las pruebas pasaron!")
    print("✅ menu_service.py está funcionando correctamente con modelos")


if __name__ == "__main__":
    test_menu_service()
