"""
Modelo de Orden
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Orden:
    """Representa una orden/pedido de una mesa"""
    id: Optional[int]
    mesa_id: int
    cliente_nombre: str
    estado: str  # 'abierta', 'cerrada'
    total: float
    fecha: datetime
    actualizado_en: Optional[datetime] = None
    cerrado_en: Optional[datetime] = None
    
    def esta_abierta(self) -> bool:
        """Verifica si la orden está abierta"""
        return self.estado == "abierta"
    
    def esta_cerrada(self) -> bool:
        """Verifica si la orden está cerrada"""
        return self.estado == "cerrada"
    
    def cerrar(self) -> None:
        """Cierra la orden"""
        self.estado = "cerrada"
        self.cerrado_en = datetime.now()
    
    def abrir(self) -> None:
        """Abre la orden (reabre si estaba cerrada)"""
        self.estado = "abierta"
        self.cerrado_en = None
    
    def actualizar_total(self, nuevo_total: float) -> None:
        """Actualiza el total de la orden"""
        self.total = nuevo_total
        self.actualizado_en = datetime.now()
    
    def get_total_formateado(self) -> str:
        """Retorna el total formateado"""
        return f"${self.total:.2f}"
    
    def __str__(self) -> str:
        return f"Orden #{self.id} - Mesa {self.mesa_id} - {self.cliente_nombre}"
