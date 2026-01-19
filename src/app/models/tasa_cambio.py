"""
Modelo de Tasa de Cambio
"""
from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class TasaCambio:
    """Representa una tasa de cambio para un día específico"""
    id: Optional[int]
    fecha: date
    tasa: float
    
    def convertir_a_bolivares(self, monto_dolares: float) -> float:
        """Convierte un monto en dólares a bolívares"""
        return monto_dolares * self.tasa
    
    def convertir_a_dolares(self, monto_bolivares: float) -> float:
        """Convierte un monto en bolívares a dólares"""
        if self.tasa == 0:
            return 0
        return monto_bolivares / self.tasa
    
    def get_tasa_formateada(self) -> str:
        """Retorna la tasa formateada"""
        return f"Bs. {self.tasa:.2f}"
    
    def __str__(self) -> str:
        return f"{self.fecha}: {self.get_tasa_formateada()}"
