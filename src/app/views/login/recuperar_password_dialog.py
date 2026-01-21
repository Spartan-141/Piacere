# src/app/views/login/recuperar_password_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services.usuarios_service import generar_token_recuperacion
from ...models import Usuario


class RecuperarPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recuperar Contraseña")
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        titulo = QLabel("Recuperar Contraseña")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #ffffff;")
        layout.addWidget(titulo)

        instrucciones = QLabel(
            "Ingresa tu dirección de email y te enviaremos un código "
            "de recuperación para restablecer tu contraseña."
        )
        instrucciones.setWordWrap(True)
        instrucciones.setAlignment(Qt.AlignCenter)
        instrucciones.setStyleSheet("color: #ffffff; font-size: 11pt;")
        layout.addWidget(instrucciones)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email")
        self.input_email.setMinimumHeight(45)
        self.input_email.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 11pt;
                
            }
        """)
        layout.addWidget(self.input_email)

        btn_enviar = QPushButton("Enviar Código de Recuperación")
        btn_enviar.setMinimumHeight(50)
        btn_enviar.setStyleSheet("""
            QPushButton {
                background-color: #800020;
                color: #F5F5DC;
                font-weight: bold;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #900028;
            }
        """)
        btn_enviar.clicked.connect(self.enviar_codigo)
        layout.addWidget(btn_enviar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(45)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                font-weight: bold;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(btn_cancelar)

        layout.addStretch()
        self.setLayout(layout)

    def enviar_codigo(self):
        email = self.input_email.text().strip()

        if not email:
            QMessageBox.warning(self, "Error", "Por favor ingresa tu email")
            return

        # Validar formato de email
        if not Usuario.validar_email(email):
            QMessageBox.warning(self, "Error", "El formato del email no es válido")
            return

        # Generar token de recuperación
        ok, err, token = generar_token_recuperacion(email)

        if not ok:
            QMessageBox.warning(self, "Error", err or "No se pudo generar el código de recuperación")
            return

        # En un sistema real, aquí se enviaría el token por email
        # Por ahora, lo mostramos en un diálogo
        self.mostrar_token(token)

    def mostrar_token(self, token):
        """Muestra el token en un diálogo (simulando envío de email)"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Código de Recuperación")
        dialog.setFixedSize(550, 350)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        titulo = QLabel("Código Generado")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #27ae60;")
        layout.addWidget(titulo)

        mensaje = QLabel(
            "Copia el código a continuación y úsalo para "
            "restablecer tu contraseña:"
        )
        mensaje.setWordWrap(True)
        mensaje.setAlignment(Qt.AlignCenter)
        mensaje.setStyleSheet("color: #ffffff; font-size: 12pt;")
        layout.addWidget(mensaje)

        token_display = QTextEdit()
        token_display.setPlainText(token)
        token_display.setReadOnly(True)
        token_display.setMaximumHeight(80)
        token_display.setStyleSheet("""
            QTextEdit {
                
                border: 2px solid #f5f5f5;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(token_display)

        btn_cerrar = QPushButton("Entendido")
        btn_cerrar.setMinimumHeight(45)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_cerrar.clicked.connect(dialog.accept)
        layout.addWidget(btn_cerrar)

        dialog.setLayout(layout)
        dialog.exec()

        # Cerrar el diálogo de recuperación y aceptar
        self.accept()
