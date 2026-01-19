from pathlib import Path
import sys
import os

# Ruta base del proyecto
# En desarrollo: carpeta del proyecto
# En ejecutable: carpeta donde está el .exe (para que la DB persista)
if getattr(sys, "frozen", False):
    # Ejecutable empaquetado: usar carpeta donde está el .exe
    BASE_DIR: Path = Path(sys.executable).parent
else:
    # Modo desarrollo: dos niveles arriba de src/app/config.py -> proyecto/
    BASE_DIR: Path = Path(__file__).resolve().parents[2]

# Carpeta de recursos (qss, iconos, imágenes)
RESOURCES_DIR: Path = BASE_DIR / "src" / "app" / "resources"

# Ruta a la base de datos (en la carpeta data/ junto al ejecutable o proyecto)
DB_PATH: Path = BASE_DIR / "data" / "restaurante.db"

# Parámetros de configuración
DEBUG: bool = os.environ.get("APP_DEBUG", "1") not in ("0", "False", "false")
LOG_LEVEL: str = os.environ.get("APP_LOG_LEVEL", "DEBUG" if DEBUG else "INFO")

# Opciones de UI / defaults
DEFAULT_WINDOW_SIZE = (1024, 768)
APP_NAME = "Sistema Restaurante"


def get_env_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val not in ("0", "False", "false")


# ✅ Función utilitaria para obtener rutas dentro de resources
def resource_path(*parts: str) -> Path:
    """
    Devuelve la ruta absoluta a un recurso, compatible con PyInstaller.
    En desarrollo: usa RESOURCES_DIR (src/app/resources/)
    En .exe: usa sys._MEIPASS/app/resources/

    Ejemplo:
        resource_path("icons", "mesa.png")
        resource_path("images", "login_image.jpg")
    """
    if getattr(sys, "frozen", False):
        # Ejecutable empaquetado por PyInstaller
        # Los recursos están en _MEIPASS/app/resources/
        base_path = Path(sys._MEIPASS) / "app" / "resources"
    else:
        # Modo desarrollo
        base_path = RESOURCES_DIR
    return base_path.joinpath(*parts)
