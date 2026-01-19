"""
Modelo de Mesa
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Mesa:
    """Representa una mesa del restaurante"""

    id: Optional[int]
    numero: str  # Nombre de la mesa (ej: "Mesa P1", "Mesa T2")
    estado: str  # 'libre', 'ocupada'
    seccion_id: int

    def esta_disponible(self) -> bool:
        """Verifica si la mesa está disponible"""
        return self.estado == "libre"

    def ocupar(self) -> None:
        """Marca la mesa como ocupada"""
        self.estado = "ocupada"

    def liberar(self) -> None:
        """Marca la mesa como libre"""
        self.estado = "libre"

    def __str__(self) -> str:
        return f"Mesa {self.numero}"
