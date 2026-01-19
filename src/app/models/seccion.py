"""
Modelo de Sección de Mesas
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Seccion:
    """Representa una sección del restaurante (Principal, Terraza, etc.)"""
    id: Optional[int]
    nombre: str
    
    def __str__(self) -> str:
        return self.nombre
