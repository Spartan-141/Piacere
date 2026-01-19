"""
Script de desarrollo con reinicio automático
Reinicia la aplicación automáticamente cuando detecta cambios en archivos .py
"""

import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time


class AppRestarter(FileSystemEventHandler):
    """Reinicia la aplicación cuando se detectan cambios"""

    def __init__(self):
        self.process = None
        self.restart_app()

    def on_modified(self, event):
        # Ignorar archivos temporales y __pycache__
        if "__pycache__" in event.src_path or event.src_path.endswith(".pyc"):
            return

        if event.src_path.endswith(".py"):
            print(f"\n🔄 Detectado cambio en {event.src_path}")
            print("🔄 Reiniciando aplicación...")
            self.restart_app()

    def restart_app(self):
        """Reinicia el proceso de la aplicación"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

        self.process = subprocess.Popen(
            [sys.executable, "run.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("✅ Aplicación iniciada")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Modo Desarrollo - Reinicio Automático Activado")
    print("=" * 60)
    print("👀 Observando cambios en src/...")
    print("💡 Presiona Ctrl+C para detener")
    print("=" * 60)

    event_handler = AppRestarter()
    observer = Observer()
    observer.schedule(event_handler, "src", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo modo desarrollo...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
        print("✅ Aplicación detenida")

    observer.join()
