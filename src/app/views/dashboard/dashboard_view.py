from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
)
from PySide6.QtCore import Qt, QTimer, QDateTime

# Configurar matplotlib para ejecutables de PyInstaller
import sys
import os

if getattr(sys, "frozen", False):
    # Estamos en un ejecutable empaquetado
    os.environ["MPLBACKEND"] = "Qt5Agg"
    import matplotlib

    matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ...services import dashboard_service


class DashboardView(QWidget):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setup_ui()

        # Timer para actualizar fecha/hora cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

        # Timer para actualizar datos cada 30 segundos
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.load_real_data)
        self.data_timer.start(30000)  # 30 segundos

        # Cargar datos reales
        self.load_real_data()

    def setup_ui(self):
        """Configura la interfaz principal del dashboard"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        top_section = self.create_top_section()
        main_layout.addWidget(top_section, stretch=2)

        middle_section = self.create_middle_section()
        main_layout.addWidget(middle_section, stretch=5)

        bottom_section = self.create_bottom_section()
        main_layout.addWidget(bottom_section, stretch=4)

    # ==========================================
    # SECCIÓN SUPERIOR
    # ==========================================

    def create_top_section(self):
        """Crea la sección superior con info de usuario y métricas"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Card de usuario (30%)
        user_card = self.create_user_card()
        layout.addWidget(user_card, stretch=3)

        # Card de métricas (70%)
        metrics_card = self.create_metrics_card()
        layout.addWidget(metrics_card, stretch=7)

        return container

    def create_user_card(self):
        """Crea la card con información del usuario"""
        card = QFrame()
        card.setObjectName("userCard")
        card.setStyleSheet(
            """
            QFrame#userCard {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 1px solid #404040;
                padding-top: 10px;
            }
        """
        )

        # Layout vertical principal
        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(8)

        # Fila superior: Avatar + Nombre/Rol
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Avatar con iniciales
        avatar = QLabel()
        avatar.setObjectName("avatar")
        initials = self.get_user_initials()
        avatar.setText(initials)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(55, 55)
        avatar.setStyleSheet(
            """
            QLabel#avatar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #42A5F5, stop:1 #1976D2);
                border-radius: 27px;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """
        )
        top_row.addWidget(avatar, alignment=Qt.AlignLeft | Qt.AlignTop)

        # Layout vertical para nombre y rol
        name_role_layout = QVBoxLayout()
        name_role_layout.setSpacing(2)

        # Nombre y apellido de usuario
        nombre_completo = self.usuario.get_nombre_completo()
        self.user_name_label = QLabel(nombre_completo)
        self.user_name_label.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            color: #ffffff;
            padding-top: 6px;
        """
        )
        name_role_layout.addWidget(self.user_name_label)

        # Rol
        role_label = QLabel(self.usuario.rol.upper())
        role_label.setStyleSheet(
            """
            font-size: 12px;
            color: #999999;
            padding-left: 6px;
        """
        )
        name_role_layout.addWidget(role_label)
        name_role_layout.addStretch()

        top_row.addLayout(name_role_layout)
        top_row.addStretch()

        main_layout.addLayout(top_row)

        # Spacer para empujar la fecha/hora hacia abajo
        main_layout.addStretch()

        # Fila inferior: Fecha y hora (alineada a la derecha)
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet(
            """
            font-size: 10px;
            color: #cccccc;
        """
        )
        self.datetime_label.setAlignment(Qt.AlignRight)
        self.update_datetime()
        bottom_row.addWidget(self.datetime_label)

        main_layout.addLayout(bottom_row)

        return card

    def create_metrics_card(self):
        """Crea la card contenedora de las 3 métricas"""
        card = QFrame()
        card.setObjectName("metricsCard")
        card.setStyleSheet(
            """
            QFrame#metricsCard {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 1px solid #404040;
                padding: 14px;
            }
        """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Métrica 1: Tasa del Día
        self.tasa_metric = self.create_metric_mini_card(
            "Tasa del Día", "0.00 Bs", "#FF9800", "#FFB74D"
        )
        layout.addWidget(self.tasa_metric)

        # Métrica 2: Órdenes del Día
        self.ordenes_metric = self.create_metric_mini_card(
            "Órdenes Hoy", "0", "#1A237E", "#3F51B5"
        )
        layout.addWidget(self.ordenes_metric)

        # Métrica 3: Ventas del Día
        self.ventas_metric = self.create_metric_mini_card(
            "Ventas Hoy", "$0.00", "#1976D2", "#42A5F5"
        )
        layout.addWidget(self.ventas_metric)

        return card

    def create_metric_mini_card(self, title, value, color1, color2):
        """Crea una mini card de métrica - SIN ICONO, PADDING REDUCIDO"""
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color1}, stop:1 {color2});
                border-radius: 12px;
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            color: #ffffff;
        """
        )
        layout.addWidget(title_label)

        # Valor
        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        value_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding: 0px 5px;
        """
        )
        layout.addWidget(value_label)

        layout.addStretch()

        # Guardar referencia
        card.value_label = value_label

        return card

    # ==========================================
    # SECCIÓN MEDIA
    # ==========================================

    def create_middle_section(self):
        """Crea la sección media con gráficos"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Card de gráfico de ventas (60%)
        sales_card = self.create_sales_chart_card()
        layout.addWidget(sales_card, stretch=6)

        # Card de estado de mesas (40%)
        tables_card = self.create_table_status_card()
        layout.addWidget(tables_card, stretch=4)

        return container

    def create_sales_chart_card(self):
        """Crea la card con el gráfico de ventas mensuales"""
        card = QFrame()
        card.setObjectName("salesChartCard")
        card.setStyleSheet(
            """
            QFrame#salesChartCard {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 1px solid #404040;
            }
        """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Título
        title = QLabel("Ventas Mensuales")
        title.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            color: #ffffff;
        """
        )
        layout.addWidget(title)

        # Gráfico
        self.sales_figure = Figure(figsize=(6, 3), facecolor="#2b2b2b")
        self.sales_canvas = FigureCanvas(self.sales_figure)
        self.sales_ax = self.sales_figure.add_subplot(111)
        layout.addWidget(self.sales_canvas)

        return card

    def create_table_status_card(self):
        """Crea la card con el gráfico de estado de mesas"""
        card = QFrame()
        card.setObjectName("tableStatusCard")
        card.setStyleSheet(
            """
            QFrame#tableStatusCard {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 1px solid #404040;
            }
        """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Título
        title = QLabel("Estado de Mesas")
        title.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            color: #ffffff;
        """
        )
        layout.addWidget(title)

        # Gráfico de dona
        self.table_figure = Figure(figsize=(3, 3), facecolor="#2b2b2b")
        self.table_canvas = FigureCanvas(self.table_figure)
        self.table_ax = self.table_figure.add_subplot(111)
        layout.addWidget(self.table_canvas, alignment=Qt.AlignCenter)

        # Labels de estado
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)

        self.libres_label = self.create_status_label("🟢 Libres:", "0")
        self.ocupadas_label = self.create_status_label("🔴 Ocupadas:", "0")
        self.reservadas_label = self.create_status_label("🟡 Reservadas:", "0")

        status_layout.addWidget(self.libres_label)
        status_layout.addWidget(self.ocupadas_label)
        status_layout.addWidget(self.reservadas_label)

        layout.addLayout(status_layout)

        return card

    def create_status_label(self, text, value):
        """Crea un label de estado con valor"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(text)
        label.setStyleSheet("font-size: 15px; color: #cccccc;")
        label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("statusValue")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(value_label)

        container.value_label = value_label
        return container

    # ==========================================
    # SECCIÓN INFERIOR
    # ==========================================

    def create_bottom_section(self):
        """Crea la sección inferior con actividad reciente"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabla de últimas facturas
        invoices_card = self.create_recent_invoices_card()
        layout.addWidget(invoices_card, stretch=7)

        # Acciones rápidas
        actions_card = self.create_quick_actions_card()
        layout.addWidget(actions_card, stretch=3)

        return container

    def create_recent_invoices_card(self):
        """Crea la card con las últimas facturas"""
        card = QFrame()
        card.setObjectName("invoicesCard")
        card.setStyleSheet(
            """
            QFrame#invoicesCard {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 1px solid #404040;
            }
        """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Título
        title = QLabel("Últimas Facturas")
        title.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            color: #ffffff;
        """
        )
        layout.addWidget(title, stretch=0)

        # Tabla - se expande para llenar el espacio disponible
        self.invoices_table = QTableWidget(0, 4)
        self.invoices_table.setHorizontalHeaderLabels(
            ["#Factura", "Cliente", "Monto", "Hora"]
        )
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invoices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.setAlternatingRowColors(True)
        # Removido setMaximumHeight para que se expanda
        layout.addWidget(self.invoices_table, stretch=1)

        return card

    def create_quick_actions_card(self):
        """Crea la card con acciones rápidas"""
        card = QFrame()
        card.setObjectName("actionsCard")
        card.setStyleSheet(
            """
            QFrame#actionsCard {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 1px solid #404040;
            }
        """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Título - sin stretch para que se quede arriba
        title = QLabel("Acciones Rápidas")
        title.setStyleSheet(
            """
            font-size: 17px;
            font-weight: bold;
            color: #ffffff;
        """
        )
        layout.addWidget(title, stretch=0)

        # Contenedor para centrar botones verticalmente
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(12)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Spacer superior para centrar
        buttons_layout.addStretch(1)

        # Botones
        btn_nueva_orden = self.create_action_button("🍽️ Nueva Orden")
        btn_nueva_orden.clicked.connect(self.abrir_nueva_orden)
        
        btn_reportes = self.create_action_button("📊 Ver Reportes")
        btn_reportes.clicked.connect(self.abrir_reportes)
        
        self.btn_tasa = self.create_action_button("💱 Actualizar Tasa")
        self.btn_tasa.clicked.connect(self.abrir_actualizar_tasa)

        buttons_layout.addWidget(btn_nueva_orden)
        buttons_layout.addWidget(btn_reportes)
        buttons_layout.addWidget(self.btn_tasa)

        # Spacer inferior para centrar
        buttons_layout.addStretch(1)

        layout.addWidget(buttons_container, stretch=1)

        return card

    def create_action_button(self, text):
        """Crea un botón de acción rápida"""
        btn = QPushButton(text)
        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 20px;
                font-size: 13px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
        """
        )
        return btn

    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================

    def get_user_initials(self):
        """Obtiene las iniciales del usuario"""
        name = self.usuario.nombre
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif len(parts) == 1:
            return parts[0][:2].upper()
        return "US"

    def update_datetime(self):
        """Actualiza la fecha y hora actual"""
        now = QDateTime.currentDateTime()
        date_str = now.toString("dddd, dd MMMM yyyy")
        time_str = now.toString("hh:mm:ss AP")
        self.datetime_label.setText(f"{date_str}\n{time_str}")

    def load_real_data(self):
        """Carga datos reales desde el servicio"""
        try:
            # Obtener tasa de cambio
            tasa = dashboard_service.get_current_exchange_rate()

            # Obtener órdenes del día
            ordenes_hoy = dashboard_service.get_today_orders_count()

            # Obtener ventas del día
            ventas = dashboard_service.get_today_sales()

            # Actualizar métricas
            self.update_metrics(tasa, ordenes_hoy, ventas["usd"], ventas["ves"])

            # Cargar gráfico de ventas mensuales
            self.load_sales_chart_real()

            # Cargar estado de mesas
            self.load_table_status_real()

            # Cargar últimas facturas
            self.load_recent_invoices_real()
            
            # Verificar estado de la tasa (si ya se registró hoy)
            # dashboard_service.get_current_exchange_rate() devuelve el valor, 
            # pero necesitamos saber si es DE HOY.
            
            # Opcion 1: Usar tasa_cambio_service directamente
            from ...services import tasa_cambio_service
            from datetime import date
            hoy = date.today().isoformat()
            tasa_hoy = tasa_cambio_service.obtener_tasa(hoy)
            
            if tasa_hoy:
                # Tasa registrada -> VERDE
                self.btn_tasa.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 15px 20px;
                        font-size: 13px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #2ecc71; }
                """)
                self.btn_tasa.setText(f"💱 Tasa Actualizada ({tasa_hoy.tasa} Bs)")
            else:
                # Tasa NO registrada -> ROJO
                self.btn_tasa.setStyleSheet("""
                    QPushButton {
                        background-color: #c0392b;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 15px 20px;
                        font-size: 13px;
                        font-weight: bold;
                        animation: pulse 2s infinite;
                    }
                    QPushButton:hover { background-color: #e74c3c; }
                """)
                self.btn_tasa.setText("⚠️ ACTUALIZAR TASA")

        except Exception as e:
            print(f"Error cargando datos del dashboard: {e}")
            # Fallback a datos de ejemplo si hay error
            self.load_placeholder_data()

    def load_placeholder_data(self):
        """Carga datos de ejemplo (fallback)"""
        self.update_metrics(39.50, 15, 1250.00, 48750.00)
        self.load_sales_chart()
        self.load_table_status(12, 8, 0)
        self.load_recent_invoices()

    def update_metrics(self, tasa, ordenes, ventas_usd, ventas_ves):
        """Actualiza los valores de las métricas"""
        self.tasa_metric.value_label.setText(f"{tasa:.2f} Bs")
        self.ordenes_metric.value_label.setText(str(ordenes))
        self.ventas_metric.value_label.setText(
            f"${ventas_usd:,.2f}\n{ventas_ves:,.2f} Bs"
        )

    def load_sales_chart(self):
        """Carga el gráfico de ventas mensuales"""
        months = [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ]
        sales = [1200, 1500, 1800, 1600, 2000, 2200, 2100, 2500, 2700, 3000, 3200, 3500]

        self.sales_ax.clear()
        bars = self.sales_ax.bar(
            months, sales, color="#42A5F5", edgecolor="#1976D2", linewidth=1.5
        )

        for bar in bars:
            bar.set_alpha(0.8)

        self.sales_ax.set_facecolor("#2b2b2b")
        self.sales_ax.tick_params(colors="#ffffff", labelsize=7)
        self.sales_ax.spines["bottom"].set_color("#404040")
        self.sales_ax.spines["left"].set_color("#404040")
        self.sales_ax.spines["top"].set_visible(False)
        self.sales_ax.spines["right"].set_visible(False)
        self.sales_ax.grid(True, alpha=0.2, color="#ffffff")
        self.sales_ax.set_ylabel("Ventas ($)", color="#ffffff", fontsize=8)

        self.sales_figure.tight_layout()
        self.sales_canvas.draw()

    def load_table_status(self, libres, ocupadas, reservadas):
        """Carga el gráfico de estado de mesas"""
        sizes = [libres, ocupadas, reservadas]
        colors = ["#4CAF50", "#F44336", "#FFC107"]

        self.table_ax.clear()

        # Crear gráfico de dona
        self.table_ax.pie(
            sizes,
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor="#2b2b2b", linewidth=2),
        )

        # Agregar texto en el centro
        total = sum(sizes)
        self.table_ax.text(
            0,
            0,
            str(total),
            ha="center",
            va="center",
            fontsize=18,
            fontweight="bold",
            color="#ffffff",
        )
        self.table_ax.text(
            0, -0.3, "Total", ha="center", va="center", fontsize=10, color="#cccccc"
        )

        self.table_figure.tight_layout()
        self.table_canvas.draw()

        # Actualizar labels
        self.libres_label.value_label.setText(str(libres))
        self.ocupadas_label.value_label.setText(str(ocupadas))
        self.reservadas_label.value_label.setText(str(reservadas))

    def load_recent_invoices(self):
        """Carga las últimas facturas"""
        invoices = [
            ("FAC-001", "Juan Pérez", "$45.00", "14:30"),
            ("FAC-002", "María García", "$32.50", "15:15"),
            ("FAC-003", "Carlos López", "$58.00", "16:00"),
            ("FAC-004", "Ana Martínez", "$22.00", "16:45"),
            ("FAC-005", "Luis Rodríguez", "$67.50", "17:20"),
        ]

        self.invoices_table.setRowCount(0)
        for factura, cliente, monto, hora in invoices:
            row = self.invoices_table.rowCount()
            self.invoices_table.insertRow(row)
            self.invoices_table.setItem(row, 0, QTableWidgetItem(factura))
            self.invoices_table.setItem(row, 1, QTableWidgetItem(cliente))
            self.invoices_table.setItem(row, 2, QTableWidgetItem(monto))
            self.invoices_table.setItem(row, 3, QTableWidgetItem(hora))

    # ==========================================
    # MÉTODOS CON DATOS REALES
    # ==========================================

    def load_sales_chart_real(self):
        """Carga el gráfico de ventas con datos reales"""
        monthly_data = dashboard_service.get_monthly_sales()

        if not monthly_data:
            # Si no hay datos, usar placeholder
            self.load_sales_chart()
            return

        months = [item[0] for item in monthly_data]
        sales = [item[1] for item in monthly_data]

        self.sales_ax.clear()
        bars = self.sales_ax.bar(
            months, sales, color="#42A5F5", edgecolor="#1976D2", linewidth=1.5
        )

        for bar in bars:
            bar.set_alpha(0.8)

        self.sales_ax.set_facecolor("#2b2b2b")
        self.sales_ax.tick_params(colors="#ffffff", labelsize=7)
        self.sales_ax.spines["bottom"].set_color("#404040")
        self.sales_ax.spines["left"].set_color("#404040")
        self.sales_ax.spines["top"].set_visible(False)
        self.sales_ax.spines["right"].set_visible(False)
        self.sales_ax.grid(True, alpha=0.2, color="#ffffff")
        self.sales_ax.set_ylabel("Ventas ($)", color="#ffffff", fontsize=8)

        self.sales_figure.tight_layout()
        self.sales_canvas.draw()

    def load_table_status_real(self):
        """Carga el estado de mesas con datos reales"""
        status = dashboard_service.get_table_status()

        libres = status.get("libre", 0)
        ocupadas = status.get("ocupado", 0)
        reservadas = status.get("reservada", 0)

        self.load_table_status(libres, ocupadas, reservadas)

    def load_recent_invoices_real(self):
        """Carga las últimas facturas con datos reales"""
        invoices = dashboard_service.get_recent_invoices()

        if not invoices:
            # Si no hay facturas, usar placeholder
            self.load_recent_invoices()
            return

        self.invoices_table.setRowCount(0)
        for invoice in invoices:
            row = self.invoices_table.rowCount()
            self.invoices_table.insertRow(row)
            self.invoices_table.setItem(row, 0, QTableWidgetItem(invoice["numero"]))
            self.invoices_table.setItem(row, 1, QTableWidgetItem(invoice["cliente"]))
            self.invoices_table.setItem(row, 2, QTableWidgetItem(invoice["monto"]))
            self.invoices_table.setItem(row, 3, QTableWidgetItem(invoice["hora"]))

    # ==========================================
    # ACCIONES RÁPIDAS
    # ==========================================

    def abrir_nueva_orden(self):
        """Abre el diálogo de orden sin mesa asignada"""
        try:
            from ..orden.orden_view import OrdenDialog

            dialog = OrdenDialog(mesa=None, parent=self)
            result = dialog.exec()

            # Recargar datos del dashboard después de cerrar el diálogo
            if result:
                self.load_real_data()
        except Exception as e:
            print(f"Error abriendo nueva orden: {e}")

    def abrir_actualizar_tasa(self):
        """Abre el diálogo para actualizar la tasa"""
        try:
            from ..main.rate_update_dialog import RateUpdateDialog
            dialog = RateUpdateDialog(parent=self)
            if dialog.exec():
                self.load_real_data() # Recargar para actualizar color del botón
        except Exception as e:
            print(f"Error abriendo dialogo tasa: {e}")

    def abrir_reportes(self):
        """Abre el diálogo de reporte diario (Cierre de Caja)"""
        try:
            from ..reportes.daily_report_dialog import DailyReportDialog
            dialog = DailyReportDialog(parent=self)
            dialog.exec()
        except Exception as e:
            print(f"Error abriendo reportes: {e}")
            import traceback
            traceback.print_exc()
