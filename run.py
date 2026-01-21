import sys
import os
from pathlib import Path
import traceback
import logging

# --- Logging básico para ver todo en consola ---
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# --- Hook global para excepciones no capturadas ---
def excepthook(exc_type, exc_value, exc_tb):
    logging.error("Excepción no capturada:", exc_info=(exc_type, exc_value, exc_tb))
    traceback.print_exception(exc_type, exc_value, exc_tb)

sys.excepthook = excepthook

# --- Instalador de handler de mensajes de Qt ---
# Esto captura mensajes como "Could not parse application stylesheet"
try:
    from PySide6.QtCore import qInstallMessageHandler, QtMsgType
    def qt_message_handler(mode, context, message):
        level = {0: "DEBUG", 1: "INFO", 2: "WARNING", 3: "CRITICAL"}.get(mode, "INFO")
        # Imprime el mensaje de Qt y un stack Python para ver el contexto
        print(f"QT-{level}: {message}")
        traceback.print_stack(limit=10)
    qInstallMessageHandler(qt_message_handler)
except Exception as e:
    # Si por alguna razón PySide6 no está disponible aún, lo logueamos y seguimos.
    logging.warning("No se pudo instalar qt_message_handler ahora: %s", e)

# Detectar si estamos en un ejecutable de PyInstaller
if getattr(sys, "frozen", False):
    application_path = Path(sys.executable).parent
    sys.path.insert(0, str(application_path))
    if hasattr(sys, "_MEIPASS"):
        os.chdir(sys._MEIPASS)
else:
    application_path = Path(__file__).parent
    src_path = application_path / "src"
    sys.path.insert(0, str(src_path))

# Ahora importar el main (se hace después de preparar handlers)
from app.main import main

if __name__ == "__main__":
    main()