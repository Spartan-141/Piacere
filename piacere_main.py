

import sys
import os
from pathlib import Path

# Configurar paths para PyInstaller
if getattr(sys, "frozen", False):
    # Ejecutando como .exe
    bundle_dir = Path(sys._MEIPASS)
    os.chdir(bundle_dir)
else:
    # Ejecutando en desarrollo
    bundle_dir = Path(__file__).parent

# Agregar src al path
src_path = bundle_dir / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Importar y ejecutar
if __name__ == "__main__":
    from PySide6.QtGui import QPalette, QColor
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTranslator, QLibraryInfo

    from app.views.login.login import LoginWindow
    from app.utils.logging_config import configure_logging
    from app.db.init_db import inicializar_base_datos
    from app.styles import DARK_STYLES

    # Configurar logging
    configure_logging()

    # Inicializar base de datos
    inicializar_base_datos()

    # Crear aplicación
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Configurar idioma
    translator = QTranslator(app)
    translator.load("qt_es", QLibraryInfo.path(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    # Paleta básica
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#303030"))
    palette.setColor(QPalette.WindowText, QColor("#ffffff"))
    palette.setColor(QPalette.Base, QColor("#1e1e1e"))
    palette.setColor(QPalette.AlternateBase, QColor("#2a2a2a"))
    palette.setColor(QPalette.Text, QColor("#ffffff"))
    palette.setColor(QPalette.Button, QColor("#353535"))
    palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
    app.setPalette(palette)

    # Aplicar estilos
    app.setStyleSheet(DARK_STYLES)

    # Crear y mostrar ventana de login
    login_window = LoginWindow()
    login_window.show()

    # Ejecutar aplicación
    sys.exit(app.exec())
