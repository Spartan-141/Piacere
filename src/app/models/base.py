"""
Clase base opcional para todos los modelos
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class BaseModel:
    """Modelo base con campos comunes"""
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones básicas después de inicialización"""
        pass
