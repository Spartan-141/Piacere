"""
Modelo de Factura
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Factura:
    """Representa una factura/comprobante de pago"""

    id: Optional[int]
    orden_id: int
    numero_factura: str
    fecha: datetime
    cliente_nombre: str
    forma_pago: str
    total: float
    total_ves: float

    def get_numero_formateado(self) -> str:
        """Retorna el número de factura formateado"""
        return f"FAC-{self.numero_factura}"

    def get_fecha_formateada(self, formato: str = "%d/%m/%Y %H:%M") -> str:
        """Retorna la fecha formateada"""
        if isinstance(self.fecha, str):
            # Si la fecha viene como string de la BD, intentar parsearla
            try:
                fecha_obj = datetime.fromisoformat(self.fecha.replace(" ", "T"))
                return fecha_obj.strftime(formato)
            except Exception:
                return self.fecha
        return self.fecha.strftime(formato)

    def get_total_formateado(self) -> str:
        """Retorna el total formateado"""
        return f"${self.total:.2f}"

    def __str__(self) -> str:
        return f"{self.get_numero_formateado()} - {self.cliente_nombre} - {self.get_total_formateado()}"
