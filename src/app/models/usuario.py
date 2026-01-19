"""
Modelo de Usuario del sistema
"""
from dataclasses import dataclass
from typing import Optional
import hashlib


@dataclass
class Usuario:
    """Representa un usuario del sistema (mesero, admin, cajero)"""
    id: Optional[int]
    nombre: str
    apellido: Optional[str]
    usuario: str  # username
    clave: str    # password (hash o plain según implementación)
    rol: str      # 'admin', 'mesero', 'cajero', 'cocinero'
    
    def es_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.rol == "admin"
    
    def puede_gestionar_usuarios(self) -> bool:
        """Verifica si puede gestionar usuarios"""
        return self.rol == "admin"
    
    def puede_tomar_ordenes(self) -> bool:
        """Verifica si puede tomar órdenes"""
        return self.rol in ["mesero", "admin"]
    
    def puede_facturar(self) -> bool:
        """Verifica si puede generar facturas"""
        return self.rol in ["cajero", "admin"]
    
    def puede_gestionar_inventario(self) -> bool:
        """Verifica si puede gestionar el inventario"""
        return self.rol == "admin"
    
    def get_nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña (opcional, para futuras mejoras)"""
        return hashlib.sha256(password.encode()).hexdigest()
