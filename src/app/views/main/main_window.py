from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout
from .ui_mainwindow import Ui_MainWindow

# Vistas
from ..mesas.mesas_view import MesasView
from ..inventario.inventario_view import InventarioView
from ..reportes.reportes_view import ReportesView
from ..conversion.tasaview import TasaView
from ..usuarios.usuarios_view import UsuariosView
from ..usuarios.mi_perfil_view import MiPerfilView
from ..dashboard.dashboard_view import DashboardView
from ..menu.menu_view import MenuView


class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        # usuario es ahora un objeto Usuario completo
        self.usuario = usuario
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ✅ Asignar layout manualmente a self.ui.main
        layout_main = QVBoxLayout(self.ui.main)
        self.ui.main.setLayout(layout_main)

        # Crear stacked widget y añadirlo al layout
        self.stacked_widget = QStackedWidget()
        layout_main.addWidget(self.stacked_widget)

        # Instanciar vistas
        self.dashboard_view = DashboardView(usuario=self.usuario)
        self.mesas_view = MesasView()
        self.menu_view = MenuView()
        self.inventario_view = InventarioView(
            es_admin=self.usuario.es_admin()
        )
        self.reportes_view = ReportesView()
        self.tasa_view = TasaView()
        
        # Vista de usuarios o perfil según el rol
        if self.usuario.es_admin():
            self.usuarios_view = UsuariosView(usuario_actual=self.usuario)
        else:
            self.usuarios_view = None
        
        # Vista de perfil personal para todos los usuarios
        self.mi_perfil_view = MiPerfilView(usuario_actual=self.usuario)

        # Añadir vistas al stacked
        self.stacked_widget.addWidget(self.dashboard_view)  # index 0
        self.stacked_widget.addWidget(self.mesas_view)  # index 1
        self.stacked_widget.addWidget(self.menu_view)  # index 2
        self.stacked_widget.addWidget(self.inventario_view)  # index 3
        self.stacked_widget.addWidget(self.reportes_view)  # index 4
        self.stacked_widget.addWidget(self.tasa_view)  # index 5
        if self.usuarios_view:
            self.stacked_widget.addWidget(self.usuarios_view)  # index 6
        self.stacked_widget.addWidget(self.mi_perfil_view)  # index 7

        # Conectar botones del sidebar
        self.ui.pushButton.clicked.connect(self.mostrar_dashboard)
        self.ui.pushButton_3.clicked.connect(self.mostrar_mesas)
        self.ui.pushButton_8.clicked.connect(self.mostrar_menu)
        self.ui.pushButton_5.clicked.connect(self.mostrar_reportes)
        self.ui.pushButton_6.clicked.connect(self.mostrar_tasa)
        
        # Botón usuarios: muestra gestión de usuarios (admin) o perfil personal (otros)
        if self.usuario.es_admin():
            self.ui.pushButton_7.clicked.connect(self.mostrar_usuarios)
            self.ui.pushButton_7.setText("Usuarios")
        else:
            self.ui.pushButton_7.clicked.connect(self.mostrar_mi_perfil)
            self.ui.pushButton_7.setText("Mi Perfil")
        
        self.ui.pushButton_9.clicked.connect(self.cerrar_sesion)

        # Vista por defecto
        self.mostrar_dashboard()

    # Métodos para cambiar vistas y actualizar el label del sidebar
    def mostrar_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_view)
        self.ui.label_2.setText("Dashboard")

    def mostrar_mesas(self):
        self.stacked_widget.setCurrentWidget(self.mesas_view)
        self.ui.label_2.setText("Mesas")
        if hasattr(self.mesas_view, "actualizar_mesas"):
            try:
                self.mesas_view.actualizar_mesas()
            except Exception:
                pass

    def mostrar_reportes(self):
        self.stacked_widget.setCurrentWidget(self.reportes_view)
        self.ui.label_2.setText("Reportes")
        if hasattr(self.reportes_view, "cargar_datos"):
            try:
                self.reportes_view.cargar_datos()
            except Exception:
                pass

    def mostrar_tasa(self):
        self.stacked_widget.setCurrentWidget(self.tasa_view)
        self.ui.label_2.setText("Tasa del Día")
        if hasattr(self.tasa_view, "cargar_historial"):
            try:
                self.tasa_view.cargar_historial()
            except Exception:
                pass

    def mostrar_usuarios(self):
        """Solo para admin"""
        if self.usuarios_view and self.usuario.es_admin():
            self.stacked_widget.setCurrentWidget(self.usuarios_view)
            self.ui.label_2.setText("Usuarios")
            if hasattr(self.usuarios_view, "cargar_usuarios"):
                try:
                    self.usuarios_view.cargar_usuarios()
                except Exception:
                    pass
    
    def mostrar_mi_perfil(self):
        """Para todos los usuarios"""
        self.stacked_widget.setCurrentWidget(self.mi_perfil_view)
        self.ui.label_2.setText("Mi Perfil")
        if hasattr(self.mi_perfil_view, "cargar_datos"):
            try:
                self.mi_perfil_view.cargar_datos()
            except Exception:
                pass

    def mostrar_menu(self):
        self.stacked_widget.setCurrentWidget(self.menu_view)
        self.ui.label_2.setText("Menú")
        if hasattr(self.menu_view, "cargar_items"):
            try:
                self.menu_view.cargar_items()
            except Exception:
                pass

    def cerrar_sesion(self):
        from ..login.login import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
