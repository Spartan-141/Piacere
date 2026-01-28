from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout
from PySide6.QtGui import QIcon
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
from ..cocina.cocina_view import CocinaView  # Importar vista de cocina
from ...config import resource_path


class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        # usuario es ahora un objeto Usuario completo
        self.usuario = usuario
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle("Piacere")
        # Establecer icono de ventana
        icon_path = resource_path("icons", "pizza.png")
        self.setWindowIcon(QIcon(str(icon_path)))

        # ✅ Asignar layout manualmente a self.ui.main
        layout_main = QVBoxLayout(self.ui.main)
        self.ui.main.setLayout(layout_main)

        # Crear stacked widget y añadirlo al layout
        self.stacked_widget = QStackedWidget()
        layout_main.addWidget(self.stacked_widget)

        # Instanciar vistas - pasando usuario para control de permisos
        self.dashboard_view = DashboardView(usuario=self.usuario)
        self.mesas_view = MesasView(usuario=self.usuario)
        self.menu_view = MenuView(usuario=self.usuario)
        self.inventario_view = InventarioView(
            es_admin=self.usuario.es_admin()
        )
        self.reportes_view = ReportesView(usuario=self.usuario)
        self.tasa_view = TasaView(usuario=self.usuario)
        self.cocina_view = CocinaView()  # Vista de cocina
        
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
        self.stacked_widget.addWidget(self.cocina_view)     # index 8

        # Configuración de botones e interfaz según rol
        self._configurar_sidebar()

        # Vista por defecto
        if self.usuario.es_cocinero():
            self.mostrar_cocina()
        else:
            self.mostrar_dashboard()

    def _configurar_sidebar(self):
        """Configura la visibilidad y conexiones del sidebar según el rol"""
        
        # Conexiones básicas para roles no-cocineros
        if not self.usuario.es_cocinero():
            self.ui.pushButton.clicked.connect(self.mostrar_dashboard)
            self.ui.pushButton_3.clicked.connect(self.mostrar_mesas)
            self.ui.pushButton_5.clicked.connect(self.mostrar_reportes)
            self.ui.pushButton_6.clicked.connect(self.mostrar_tasa)
            
            # Botón Menú
            if self.usuario.puede_modificar_menu():
                self.ui.pushButton_8.clicked.connect(self.mostrar_menu)
            else:
                self.ui.pushButton_8.setVisible(False)
        else:
            # Si es cocinero, ocultamos casi todo y reusamos botones
            self.ui.pushButton.setVisible(False)   # Dashboard
            self.ui.pushButton_3.setVisible(False) # Mesas
            self.ui.pushButton_5.setVisible(False) # Reportes
            self.ui.pushButton_6.setVisible(False) # Tasa
            self.ui.pushButton_8.setVisible(False) # Menu
            
            # Reusar un botón para "Cocina" (usaremos el primero disponible)
            self.ui.pushButton.setVisible(True)
            self.ui.pushButton.setText("Cocina")
            self.ui.pushButton.clicked.connect(self.mostrar_cocina)
        
        # Botón usuarios/perfil
        if self.usuario.es_admin():
            self.ui.pushButton_7.clicked.connect(self.mostrar_usuarios)
            self.ui.pushButton_7.setText("Usuarios")
        else:
            self.ui.pushButton_7.clicked.connect(self.mostrar_mi_perfil)
            self.ui.pushButton_7.setText("Mi Perfil")
        
        self.ui.pushButton_9.clicked.connect(self.cerrar_sesion)

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
    
    def mostrar_cocina(self):
        self.stacked_widget.setCurrentWidget(self.cocina_view)
        self.ui.label_2.setText("Cocina")
        if hasattr(self.cocina_view, "refrescar"):
            try:
                self.cocina_view.refrescar()
            except Exception:
                pass

    def cerrar_sesion(self):
        from ..login.login import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
