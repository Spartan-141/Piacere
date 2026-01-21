# src/app/views/login/restablecer_password_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services.usuarios_service import restablecer_contrasena


class RestablecerPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Restablecer Contraseña")
        self.setFixedSize(500, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        titulo = QLabel("Restablecer Contraseña")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #ffffff;")
        layout.addWidget(titulo)

        instrucciones = QLabel(
            "Ingresa el código de recuperación que recibiste "
            "y tu nueva contraseña."
        )
        instrucciones.setWordWrap(True)
        instrucciones.setAlignment(Qt.AlignCenter)
        instrucciones.setStyleSheet("color: #ffffff; font-size: 11pt;")
        layout.addWidget(instrucciones)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.input_token = QLineEdit()
        self.input_token.setPlaceholderText("Código de recuperación")
        self.input_token.setMinimumHeight(45)
        self.input_token.setStyleSheet("padding: 10px; border-radius: 5px;")

        self.input_nueva_clave = QLineEdit()
        self.input_nueva_clave.setPlaceholderText("Nueva contraseña")
        self.input_nueva_clave.setEchoMode(QLineEdit.Password)
        self.input_nueva_clave.setMinimumHeight(45)
        self.input_nueva_clave.setStyleSheet("padding: 10px; border-radius: 5px;")

        self.input_confirmar_clave = QLineEdit()
        self.input_confirmar_clave.setPlaceholderText("Confirmar contraseña")
        self.input_confirmar_clave.setEchoMode(QLineEdit.Password)
        self.input_confirmar_clave.setMinimumHeight(45)
        self.input_confirmar_clave.setStyleSheet("padding: 10px; border-radius: 5px;")

        form_layout.addRow("Código:", self.input_token)
        form_layout.addRow("Nueva Contraseña:", self.input_nueva_clave)
        form_layout.addRow("Confirmar:", self.input_confirmar_clave)

        layout.addLayout(form_layout)

        btn_restablecer = QPushButton("Restablecer Contraseña")
        btn_restablecer.setMinimumHeight(50)
        btn_restablecer.setStyleSheet("""
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
        btn_restablecer.clicked.connect(self.restablecer)
        layout.addWidget(btn_restablecer)

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

    def restablecer(self):
        token = self.input_token.text().strip()
        nueva_clave = self.input_nueva_clave.text()
        confirmar = self.input_confirmar_clave.text()

        if not token or not nueva_clave or not confirmar:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return

        if nueva_clave != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return

        if len(nueva_clave) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
            return

        # Restablecer la contraseña
        ok, err = restablecer_contrasena(token, nueva_clave)

        if not ok:
            QMessageBox.critical(self, "Error", err or "No se pudo restablecer la contraseña")
            return

        QMessageBox.information(
            self,
            "Éxito",
            "Tu contraseña ha sido restablecida correctamente.\n"
            "Ahora puedes iniciar sesión con tu nueva contraseña."
        )
        self.accept()
