# src/app/services/cocina_service.py
"""
Servicio para gestionar el flujo de órdenes en la cocina
"""
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from ..db.connection import ConnectionManager


def obtener_ordenes_para_cocina() -> List[Dict]:
    """
    Obtiene todas las órdenes abiertas con sus detalles para la vista de cocina.
    Agrupa por orden y incluye información de mesa y tiempo transcurrido.
    Retorna lista de diccionarios con estructura:
    {
        'orden_id': int,
        'mesa_nombre': str,
        'cliente_nombre': str,
        'fecha': str,
        'minutos_transcurridos': int,
        'items': [
            {
                'detalle_id': int,
                'nombre': str,
                'cantidad': int,
                'estado_cocina': str
            }
        ]
    }
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        
        # Obtener órdenes abiertas con items que no estén todos listos
        cur.execute("""
            SELECT DISTINCT 
                o.id as orden_id,
                m.numero as mesa_nombre,
                o.cliente_nombre,
                o.fecha
            FROM ordenes o
            JOIN mesas m ON o.mesa_id = m.id
            JOIN orden_detalles od ON o.id = od.orden_id
            WHERE o.estado = 'abierta'
            AND od.estado_cocina != 'listo'
            ORDER BY o.fecha ASC
        """)
        ordenes_rows = cur.fetchall()
        
        result = []
        for orden_row in ordenes_rows:
            orden_id, mesa_nombre, cliente_nombre, fecha_str = orden_row
            
            # Calcular tiempo transcurrido
            try:
                if isinstance(fecha_str, str):
                    fecha = datetime.fromisoformat(fecha_str.replace(' ', 'T'))
                else:
                    fecha = fecha_str
                minutos = int((datetime.now() - fecha).total_seconds() / 60)
            except:
                minutos = 0
            
            # Obtener detalles de esta orden
            cur.execute("""
                SELECT 
                    od.id as detalle_id,
                    COALESCE(mi.nombre, 'Item #' || od.menu_item_id) as nombre,
                    od.cantidad,
                    COALESCE(od.estado_cocina, 'pendiente') as estado_cocina
                FROM orden_detalles od
                LEFT JOIN menu_items mi ON od.menu_item_id = mi.id
                WHERE od.orden_id = ?
                ORDER BY od.id
            """, (orden_id,))
            
            items = []
            for detalle_row in cur.fetchall():
                items.append({
                    'detalle_id': detalle_row[0],
                    'nombre': detalle_row[1],
                    'cantidad': detalle_row[2],
                    'estado_cocina': detalle_row[3] or 'pendiente'
                })
            
            result.append({
                'orden_id': orden_id,
                'mesa_nombre': mesa_nombre,
                'cliente_nombre': cliente_nombre,
                'fecha': fecha_str,
                'minutos_transcurridos': minutos,
                'items': items
            })
        
        return result


def cambiar_estado_item(detalle_id: int, nuevo_estado: str) -> Tuple[bool, Optional[str]]:
    """
    Cambia el estado de un item específico.
    Estados válidos: 'pendiente', 'preparando', 'listo'
    """
    estados_validos = ['pendiente', 'preparando', 'listo']
    if nuevo_estado not in estados_validos:
        return False, f"Estado inválido. Debe ser: {', '.join(estados_validos)}"
    
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE orden_detalles SET estado_cocina = ? WHERE id = ?",
                (nuevo_estado, detalle_id)
            )
            conn.commit()
            
            if cur.rowcount == 0:
                return False, "Item no encontrado"
            
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)


def marcar_preparando(detalle_id: int) -> Tuple[bool, Optional[str]]:
    """Marca un item como 'en preparación'"""
    return cambiar_estado_item(detalle_id, 'preparando')


def marcar_listo(detalle_id: int) -> Tuple[bool, Optional[str]]:
    """Marca un item como 'listo para servir'"""
    return cambiar_estado_item(detalle_id, 'listo')


def marcar_todos_preparando(orden_id: int) -> Tuple[bool, Optional[str]]:
    """Marca todos los items pendientes de una orden como 'preparando'"""
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """UPDATE orden_detalles 
                   SET estado_cocina = 'preparando' 
                   WHERE orden_id = ? AND estado_cocina = 'pendiente'""",
                (orden_id,)
            )
            conn.commit()
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)


def marcar_todos_listos(orden_id: int) -> Tuple[bool, Optional[str]]:
    """Marca todos los items de una orden como 'listo'"""
    with ConnectionManager() as conn:
        try:
            cur = conn.cursor()
            cur.execute(
                """UPDATE orden_detalles 
                   SET estado_cocina = 'listo' 
                   WHERE orden_id = ? AND estado_cocina != 'listo'""",
                (orden_id,)
            )
            conn.commit()
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)


def obtener_conteo_estados() -> Dict[str, int]:
    """
    Obtiene el conteo de items por estado para mostrar en el header.
    Retorna: {'pendiente': N, 'preparando': N, 'listo': N}
    """
    with ConnectionManager() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(od.estado_cocina, 'pendiente') as estado, COUNT(*) as count
            FROM orden_detalles od
            JOIN ordenes o ON od.orden_id = o.id
            WHERE o.estado = 'abierta'
            GROUP BY COALESCE(od.estado_cocina, 'pendiente')
        """)
        
        result = {'pendiente': 0, 'preparando': 0, 'listo': 0}
        for estado, count in cur.fetchall():
            if estado in result:
                result[estado] = count
        
        return result
