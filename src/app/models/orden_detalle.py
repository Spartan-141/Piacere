"""
Modelo de Detalle de Orden
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class OrdenDetalle:
    """Representa un item/línea de una orden"""
    id: Optional[int]
    orden_id: int
    menu_item_id: Optional[int]  # Referencia al item del menú
    variant_id: Optional[int]     # Referencia a la variante (si aplica)
    cantidad: int
    precio: float                 # Campo legacy para compatibilidad
    precio_unitario: Optional[float]  # Precio unitario explícito
    subtotal: float
    estado_cocina: str = "pendiente"  # 'pendiente', 'preparando', 'listo'
    
    def get_precio_efectivo(self) -> float:
        """Retorna el precio efectivo (precio_unitario o precio legacy)"""
        return self.precio_unitario if self.precio_unitario is not None else self.precio
    
    def calcular_subtotal(self) -> float:
        """Calcula el subtotal basado en cantidad y precio"""
        return self.cantidad * self.get_precio_efectivo()
    
    def actualizar_subtotal(self) -> None:
        """Actualiza el subtotal automáticamente"""
        self.subtotal = self.calcular_subtotal()
    
    def get_subtotal_formateado(self) -> str:
        """Retorna el subtotal formateado"""
        return f"${self.subtotal:.2f}"
    
    # Métodos para control de cocina
    def esta_pendiente(self) -> bool:
        """Verifica si el item está pendiente de preparación"""
        return self.estado_cocina == "pendiente"
    
    def esta_preparando(self) -> bool:
        """Verifica si el item está en preparación"""
        return self.estado_cocina == "preparando"
    
    def esta_listo(self) -> bool:
        """Verifica si el item está listo para servir"""
        return self.estado_cocina == "listo"
    
    def marcar_preparando(self) -> None:
        """Marca el item como en preparación"""
        self.estado_cocina = "preparando"
    
    def marcar_listo(self) -> None:
        """Marca el item como listo"""
        self.estado_cocina = "listo"
    
    def __str__(self) -> str:
        return f"{self.cantidad}x - {self.get_subtotal_formateado()}"

