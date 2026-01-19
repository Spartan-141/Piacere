"""
Modelo de Producto (Inventario - Independiente del Menú)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    """Representa un producto del inventario (independiente del menú)"""
    id: Optional[int]
    nombre: str
    descripcion: Optional[str]
    stock: int
    precio: float
    
    def tiene_stock(self, cantidad: int = 1) -> bool:
        """Verifica si hay stock suficiente"""
        return self.stock >= cantidad
    
    def reducir_stock(self, cantidad: int) -> bool:
        """
        Reduce el stock del producto
        Retorna True si se pudo reducir, False si no hay suficiente stock
        """
        if self.tiene_stock(cantidad):
            self.stock -= cantidad
            return True
        return False
    
    def aumentar_stock(self, cantidad: int) -> None:
        """Aumenta el stock del producto"""
        self.stock += cantidad
    
    def get_precio_formateado(self) -> str:
        """Retorna el precio formateado"""
        return f"${self.precio:.2f}"
    
    def __str__(self) -> str:
        return f"{self.nombre} (Stock: {self.stock})"
