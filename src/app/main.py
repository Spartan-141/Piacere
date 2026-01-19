import sys
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLibraryInfo

from .views.login.login import LoginWindow
from .utils.logging_config import configure_logging
from .db.init_db import inicializar_base_datos
from .styles import DARK_STYLES
#from .utils.hot_reload import setup_hot_reload


def main():
    configure_logging()
    inicializar_base_datos()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 🔥 Activar hot reload para estilos
    #observer = setup_hot_reload(app)

    # 🟡 Configurar idioma
    translator = QTranslator(app)
    translator.load("qt_es", QLibraryInfo.path(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    # Paleta básica (opcional si usas estilos)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#303030"))
    palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.Text, QColor("#000000"))
    app.setPalette(palette)

    # ✅ Aplicar estilos desde styles.py
    app.setStyleSheet(DARK_STYLES)

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
