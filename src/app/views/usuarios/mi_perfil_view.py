# src/app/views/usuarios/mi_perfil_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFormLayout, QFrame, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services.usuarios_service import actualizar_usuario


class MiPerfilView(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Título
        titulo = QLabel("MI PERFIL")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Información del usuario (solo lectura)
        info_group = QGroupBox("Información de la Cuenta")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                border: 2px solid #800020;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        info_layout = QFormLayout()
        info_layout.setSpacing(12)

        # Usuario (solo lectura)
        self.label_usuario = QLabel(self.usuario_actual.usuario)
        self.label_usuario.setStyleSheet("font-size: 9pt; padding: 6px; background-color: #2b2b2b; border-radius: 4px;")
        info_layout.addRow("Usuario:", self.label_usuario)
        

        # Rol (solo lectura)
        self.label_rol = QLabel(self.usuario_actual.rol.upper())
        self.label_rol.setStyleSheet("font-size: 9pt; padding: 6px; background-color: #2b2b2b; border-radius: 4px; font-weight: bold;")
        info_layout.addRow("Rol:", self.label_rol)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Datos editables
        datos_group = QGroupBox("Datos Personales")
        datos_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        datos_layout = QFormLayout()
        datos_layout.setSpacing(12)

        self.input_nombre = QLineEdit(self.usuario_actual.nombre)
        self.input_nombre.setMinimumHeight(20)
        self.input_nombre.setStyleSheet("padding: 2px; font-size: 9pt; border-radius: 4px; background-color: #2b2b2b;")

        self.input_apellido = QLineEdit(self.usuario_actual.apellido or "")
        self.input_apellido.setMinimumHeight(20)
        self.input_apellido.setStyleSheet("padding: 2px; font-size: 9pt; border-radius: 4px; background-color: #2b2b2b;")

        self.input_email = QLineEdit(self.usuario_actual.email or "")
        self.input_email.setPlaceholderText("correo@ejemplo.com")
        self.input_email.setMinimumHeight(20)
        self.input_email.setStyleSheet("padding: 2px; font-size: 9pt; border-radius: 4px; background-color: #2b2b2b;")

        datos_layout.addRow("Nombre:", self.input_nombre)
        datos_layout.addRow("Apellido:", self.input_apellido)
        datos_layout.addRow("Email:", self.input_email)

        datos_group.setLayout(datos_layout)
        layout.addWidget(datos_group)

        # Cambiar contraseña
        password_group = QGroupBox("Cambiar Contraseña")
        password_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        password_layout = QFormLayout()
        password_layout.setSpacing(12)

        self.input_nueva_clave = QLineEdit()
        self.input_nueva_clave.setPlaceholderText("Dejar vacío para no cambiar")
        self.input_nueva_clave.setEchoMode(QLineEdit.Password)
        self.input_nueva_clave.setMinimumHeight(30)
        self.input_nueva_clave.setStyleSheet("padding: 6px; font-size: 9pt; border-radius: 4px; background-color: #2b2b2b;")

        self.input_confirmar_clave = QLineEdit()
        self.input_confirmar_clave.setPlaceholderText("Confirmar nueva contraseña")
        self.input_confirmar_clave.setEchoMode(QLineEdit.Password)
        self.input_confirmar_clave.setMinimumHeight(30)
        self.input_confirmar_clave.setStyleSheet("padding: 6px; font-size: 9pt; border-radius: 4px; background-color: #2b2b2b;")

        password_layout.addRow("Nueva Contraseña:", self.input_nueva_clave)
        password_layout.addRow("Confirmar:", self.input_confirmar_clave)

        password_group.setLayout(password_layout)
        layout.addWidget(password_group)

        # Botón guardar
        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.setMinimumHeight(55)
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #F5F5DC;
                font-weight: bold;
                font-size: 13pt;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_guardar.clicked.connect(self.guardar_cambios)
        layout.addWidget(btn_guardar)

        layout.addStretch()
        self.setLayout(layout)

    def cargar_datos(self):
        """Recarga los datos del usuario actual"""
        from ...services.usuarios_service import obtener_usuario_por_id
        
        usuario_actualizado = obtener_usuario_por_id(self.usuario_actual.id)
        if usuario_actualizado:
            self.usuario_actual = usuario_actualizado
            self.input_nombre.setText(self.usuario_actual.nombre)
            self.input_apellido.setText(self.usuario_actual.apellido or "")
            self.input_email.setText(self.usuario_actual.email or "")
            self.label_usuario.setText(self.usuario_actual.usuario)
            self.label_rol.setText(self.usuario_actual.rol.upper())
            # Limpiar campos de contraseña
            self.input_nueva_clave.clear()
            self.input_confirmar_clave.clear()

    def guardar_cambios(self):
        from ...models import Usuario as UsuarioModel
        
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        email = self.input_email.text().strip() or None
        nueva_clave = self.input_nueva_clave.text()
        confirmar = self.input_confirmar_clave.text()

        # Validaciones
        if not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios")
            return

        if email and not UsuarioModel.validar_email(email):
            QMessageBox.warning(self, "Error", "El formato del email no es válido")
            return

        if nueva_clave or confirmar:
            if nueva_clave != confirmar:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
                return
            
            if len(nueva_clave) < 4:
                QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
                return

        # Actualizar usuario (sin cambiar usuario ni rol)
        ok, err = actualizar_usuario(
            self.usuario_actual.id,
            nombre,
            apellido,
            self.usuario_actual.usuario,  # No cambiar usuario
            nueva_clave or None,
            self.usuario_actual.rol,  # No cambiar rol
            email
        )

        if ok:
            QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente")
            # Actualizar datos locales
            self.usuario_actual.nombre = nombre
            self.usuario_actual.apellido = apellido
            self.usuario_actual.email = email
            # Limpiar campos de contraseña
            self.input_nueva_clave.clear()
            self.input_confirmar_clave.clear()
        else:
            QMessageBox.critical(self, "Error", err or "No se pudo actualizar el perfil")
