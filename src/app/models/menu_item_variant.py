"""
Modelo de Variante de Item del Menú
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class MenuItemVariant:
    """Representa una variante de un item del menú (Pequeña, Mediana, Grande, etc.)"""
    id: Optional[int]
    menu_item_id: int
    clave: str  # Identificador único de la variante
    nombre: str  # Nombre descriptivo (ej: "Grande", "Con extra queso")
    precio: float
    sku: Optional[str]
    position: int
    active: bool
    
    def esta_activa(self) -> bool:
        """Verifica si la variante está activa"""
        return self.active
    
    def get_precio_formateado(self) -> str:
        """Retorna el precio formateado"""
        return f"${self.precio:.2f}"
    
    def __str__(self) -> str:
        return f"{self.nombre} - {self.get_precio_formateado()}"
