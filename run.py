import sys
import os
from pathlib import Path

# Detectar si estamos en un ejecutable de PyInstaller
if getattr(sys, "frozen", False):
    # Estamos en un ejecutable empaquetado
    application_path = Path(sys.executable).parent
    # Agregar el directorio base al path
    sys.path.insert(0, str(application_path))
    # PyInstaller desempaqueta en _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        os.chdir(sys._MEIPASS)
else:
    # Estamos en desarrollo
    application_path = Path(__file__).parent
    src_path = application_path / "src"
    sys.path.insert(0, str(src_path))

# Ahora importar el main
from app.main import main

if __name__ == "__main__":
    main()
