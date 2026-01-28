# src/app/views/usuarios/editar_usuario_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QHBoxLayout, QPushButton, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services.usuarios_service import actualizar_usuario
from ...models import Usuario


class EditarUsuarioDialog(QDialog):
    def __init__(self, usuario: Usuario, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Usuario")
        self.usuario = usuario  # Ahora es un objeto Usuario
        self.setFixedSize(600, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("EDITAR USUARIO")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #ffffff;")
        layout.addWidget(titulo)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Usar atributos del objeto Usuario
        self.input_nombre = QLineEdit(self.usuario.nombre or "")
        self.input_nombre.setMinimumHeight(45)
        self.input_nombre.setStyleSheet("padding: 10px; background-color: #000000;")

        self.input_apellido = QLineEdit(self.usuario.apellido or "")
        self.input_apellido.setMinimumHeight(45)
        self.input_apellido.setStyleSheet("padding: 10px; background-color: #000000;")

        self.input_email = QLineEdit(self.usuario.email or "")
        self.input_email.setPlaceholderText("Email (opcional)")
        self.input_email.setMinimumHeight(45)
        self.input_email.setStyleSheet("padding: 10px; background-color: #000000;")

        self.input_usuario = QLineEdit(self.usuario.usuario)
        self.input_usuario.setMinimumHeight(45)
        self.input_usuario.setStyleSheet("padding: 10px; background-color: #000000;")

        self.input_clave = QLineEdit()
        self.input_clave.setPlaceholderText("Dejar vacío para no cambiar")
        self.input_clave.setEchoMode(QLineEdit.Password)
        self.input_clave.setMinimumHeight(45)
        self.input_clave.setStyleSheet("padding: 10px; background-color: #000000;")

        self.input_confirmar_clave = QLineEdit()
        self.input_confirmar_clave.setPlaceholderText("Confirmar contraseña")
        self.input_confirmar_clave.setEchoMode(QLineEdit.Password)
        self.input_confirmar_clave.setMinimumHeight(45)
        self.input_confirmar_clave.setStyleSheet("padding: 10px; background-color: #000000;")

        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["admin", "cajero", "mesero", "cocinero"])
        self.combo_rol.setCurrentText(self.usuario.rol)
        self.combo_rol.setMinimumHeight(45)
        self.combo_rol.setStyleSheet("padding: 10px; background-color: #000000;")

        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Apellido:", self.input_apellido)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Usuario:", self.input_usuario)
        form_layout.addRow("Nueva Contraseña:", self.input_clave)
        form_layout.addRow("Confirmar:", self.input_confirmar_clave)
        form_layout.addRow("Rol:", self.combo_rol)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.setMinimumHeight(50)
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #333333;
                font-weight: bold;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_guardar.clicked.connect(self.validar_edicion)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(50)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #333333;
                font-weight: bold;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)

        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_guardar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def validar_edicion(self):
        from ...models import Usuario as UsuarioModel
        
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        email = self.input_email.text().strip() or None
        usuario = self.input_usuario.text().strip()
        clave = self.input_clave.text()
        confirmar = self.input_confirmar_clave.text()
        rol = self.combo_rol.currentText()

        if not nombre or not apellido or not usuario:
            QMessageBox.warning(self, "Error", "Nombre, apellido y usuario son obligatorios")
            return

        # Validar email si se proporciona
        if email and not UsuarioModel.validar_email(email):
            QMessageBox.warning(self, "Error", "El formato del email no es válido")
            return

        if clave and clave != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
            return

        if clave and len(clave) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
            return

        # Actualizar usuario
        ok, err = actualizar_usuario(self.usuario.id, nombre, apellido, usuario, clave or None, rol, email)

        if ok:
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", err or "El nombre de usuario ya está en uso o hubo un error")