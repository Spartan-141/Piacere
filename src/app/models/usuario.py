"""
Modelo de Usuario del sistema
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import re

try:
    import bcrypt
except ImportError:
    bcrypt = None


@dataclass
class Usuario:
    """Representa un usuario del sistema (mesero, admin, cajero)"""
    id: Optional[int]
    nombre: str
    apellido: Optional[str]
    usuario: str  # username
    clave: str    # password (hash)
    rol: str      # 'admin', 'mesero', 'cajero', 'cocinero'
    email: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expiry: Optional[datetime] = None
    
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
        """Hashea una contraseña usando bcrypt"""
        if bcrypt:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback a SHA256 si bcrypt no está disponible
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifica una contraseña contra su hash"""
        if bcrypt and hashed.startswith('$2'):
            # Es un hash de bcrypt
            try:
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            except:
                return False
        else:
            # Fallback para hashes SHA256 antiguos o cuando bcrypt no está disponible
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida el formato de un email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
