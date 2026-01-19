"""
Modelo de Sección del Menú
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class MenuSection:
    """Representa una sección del menú (Pizzas, Bebidas, Postres, etc.)"""
    id: Optional[int]
    nombre: str
    descripcion: Optional[str]
    position: int
    active: bool
    
    def esta_activa(self) -> bool:
        """Verifica si la sección está activa"""
        return self.active
    
    def __str__(self) -> str:
        return self.nombre
