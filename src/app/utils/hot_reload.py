"""
Hot reload para estilos de PySide6
Permite ver cambios en tiempo real sin reiniciar la aplicación
Solo soporta styles.py (ui_*.py requiere reinicio completo)
"""

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PySide6.QtWidgets import QApplication


class StyleReloader(FileSystemEventHandler):
    """Recarga los estilos cuando se detectan cambios en styles.py"""

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app

    def on_modified(self, event):
        # Ignorar directorios y archivos temporales
        if event.is_directory or "__pycache__" in event.src_path:
            return

        file_path = Path(event.src_path)

        # Solo detectar cambios en styles.py
        # NOTA: ui_*.py deshabilitado (recargar UI causa crashes)
        if file_path.name == "styles.py":
            print(f"🔄 Detectado cambio en {file_path.name}")
            self.reload_global_styles()

    def reload_global_styles(self):
        """Recarga el módulo de estilos globales y aplica los cambios"""
        try:
            import importlib
            from app import styles

            importlib.reload(styles)

            # Aplicar los nuevos estilos globales (usa DARK_STYLES)
            self.app.setStyleSheet(styles.DARK_STYLES)
            print("✅ Estilos globales recargados exitosamente")

        except Exception as e:
            print(f"❌ Error al recargar estilos globales: {e}")
            import traceback

            traceback.print_exc()


def setup_hot_reload(app: QApplication):
    """
    Configura el hot reload para la aplicación

    Args:
        app: Instancia de QApplication

    Returns:
        Observer: El observador de archivos
    """
    # Obtener la ruta del directorio app/
    app_path = Path(__file__).parent.parent  # Subir de utils/ a app/

    # Crear el observador
    event_handler = StyleReloader(app)
    observer = Observer()

    # Observar el directorio app/ (para styles.py)
    observer.schedule(event_handler, str(app_path), recursive=False)

    observer.start()

    print("🔥 Hot reload activado")
    print("   📁 Observando: styles.py")
    print("   ⚠️  NOTA: Para cambios en ui_*.py usa 'python dev.py'")
    print("   ✨ Los cambios en styles.py se aplicarán automáticamente")

    return observer
