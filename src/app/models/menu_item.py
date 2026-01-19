"""
Modelo de Item del Menú
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class MenuItem:
    """Representa un item del menú (sin manejo de stock)"""
    id: Optional[int]
    section_id: int
    nombre: str
    descripcion: Optional[str]
    precio: float
    disponible: bool  # Disponibilidad manual, NO automática por stock
    position: int
    created_at: Optional[datetime] = None
    
    def esta_disponible(self) -> bool:
        """Verifica si el item está disponible"""
        return self.disponible
    
    def marcar_no_disponible(self) -> None:
        """Marca el item como no disponible"""
        self.disponible = False
    
    def marcar_disponible(self) -> None:
        """Marca el item como disponible"""
        self.disponible = True
    
    def get_precio_formateado(self) -> str:
        """Retorna el precio formateado"""
        return f"${self.precio:.2f}"
    
    def __str__(self) -> str:
        return self.nombre
