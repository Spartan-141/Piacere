from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QDateEdit,
    QGroupBox,
    QFrame,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
import csv
from datetime import datetime, timedelta

from ...services.factura_service import (
    obtener_facturas_rango,
    eliminar_factura,
    obtener_detalles_factura,
)
from ...services import reportes_service
from ...models import Factura
from .invoice_detail_dialog import InvoiceDetailDialog
from .invoice_print_dialog import InvoicePrintDialog


class ReportesView(QWidget):
    def __init__(self, usuario=None, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Título
        titulo = QLabel("MÓDULO DE REPORTES")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Pestañas
        self.tabs = QTabWidget()
        self.tabs.addTab(self.crear_tab_facturas(), "📄 Facturas")
        self.tabs.addTab(self.crear_tab_ventas(), "💰 Ventas")
        self.tabs.addTab(self.crear_tab_productos(), "🍽️ Productos")

        main_layout.addWidget(self.tabs)

    # ==========================================
    # TAB: FACTURAS
    # ==========================================

    def crear_tab_facturas(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Búsqueda y acciones
        search_layout = QHBoxLayout()
        search_layout.setObjectName("search_layout")
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Buscar por cliente o número de factura...")  
        self.input_cliente.textChanged.connect(self.buscar_por_cliente)
        btn_refrescar = QPushButton("Refrescar")
        btn_refrescar.clicked.connect(self.cargar_facturas)
        btn_imprimir = QPushButton("🖨️ Imprimir Factura")
        btn_imprimir.clicked.connect(self.imprimir_factura_seleccionada)

        search_layout.addWidget(self.input_cliente)
        search_layout.addWidget(btn_refrescar)
        search_layout.addWidget(btn_imprimir)
        
        # Botón eliminar - solo para admin
        puede_eliminar = self.usuario.puede_eliminar_facturas() if self.usuario else True
        if puede_eliminar:
            btn_eliminar = QPushButton("Eliminar Seleccionada")
            btn_eliminar.clicked.connect(self.eliminar_factura_seleccionada)
            search_layout.addWidget(btn_eliminar)
        
        layout.addLayout(search_layout)

        # Tabla
        self.table_facturas = QTableWidget(0, 5)
        self.table_facturas.setHorizontalHeaderLabels(
            ["Número", "Fecha", "Cliente", "Total USD", "Total Bs"]
        )
        self.table_facturas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_facturas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_facturas.setAlternatingRowColors(True)
        self.table_facturas.itemDoubleClicked.connect(self.ver_detalles_factura)
        layout.addWidget(self.table_facturas)

        # Cargar datos
        self.cargar_facturas()

        return tab

    def cargar_facturas(self):
        try:
            facturas = obtener_facturas_rango("2000-01-01", "2050-12-31")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error consultando facturas: {e}")
            return

        self.table_facturas.setRowCount(0)
        for factura in facturas:
            ridx = self.table_facturas.rowCount()
            self.table_facturas.insertRow(ridx)

            valores = [
                factura.numero_factura,
                factura.fecha,
                factura.cliente_nombre,
                factura.get_total_formateado(),
                f"{factura.total_ves:,.2f} Bs" if factura.total_ves is not None else "0.00 Bs",
            ]

            for col, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 0:
                    item.setData(Qt.UserRole, factura.id)
                self.table_facturas.setItem(ridx, col, item)

    def buscar_por_cliente(self):
        termino = self.input_cliente.text().strip()
        if not termino:
            self.cargar_facturas()
            return
        try:
            from ...services.factura_service import buscar_facturas
            facturas = buscar_facturas(termino)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error buscando facturas: {e}")
            return

        self.table_facturas.setRowCount(0)
        for factura in facturas:
            ridx = self.table_facturas.rowCount()
            self.table_facturas.insertRow(ridx)
            valores = [
                factura.numero_factura,
                factura.fecha,
                factura.cliente_nombre,
                factura.get_total_formateado(),
                f"{factura.total_ves:,.2f} Bs" if factura.total_ves is not None else "0.00 Bs",
            ]
            for col, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                if col == 0:
                    item.setData(Qt.UserRole, factura.id)
                self.table_facturas.setItem(ridx, col, item)

    def eliminar_factura_seleccionada(self):
        row = self.table_facturas.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione una factura")
            return

        factura_id = self.table_facturas.item(row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar la factura #{factura_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        ok, err = eliminar_factura(factura_id)
        if not ok:
            QMessageBox.critical(self, "Error", err or "No se pudo eliminar")
        else:
            QMessageBox.information(self, "Éxito", "Factura eliminada")
            self.cargar_facturas()

    def ver_detalles_factura(self, item):
        row = item.row()
        factura_id = self.table_facturas.item(row, 0).data(Qt.UserRole)
        dialog = InvoiceDetailDialog(factura_id, self)
        dialog.exec()

    def imprimir_factura_seleccionada(self):
        """Abre el diálogo de impresión para la factura seleccionada"""
        row = self.table_facturas.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione una factura para imprimir")
            return

        try:
            # Obtener datos de la factura
            # Obtener datos de la factura
            factura_id = self.table_facturas.item(row, 0).data(Qt.UserRole)
            numero_factura = self.table_facturas.item(row, 0).text()
            fecha = self.table_facturas.item(row, 1).text()
            cliente = self.table_facturas.item(row, 2).text()
            total_text = self.table_facturas.item(row, 3).text()

            # Obtener factura completa para forma_pago y total_ves
            from ...services.factura_service import obtener_factura_por_id

            factura = obtener_factura_por_id(factura_id)
            if not factura:
                QMessageBox.critical(self, "Error", "No se pudo obtener la factura")
                return

            # Obtener detalles de la factura
            items = obtener_detalles_factura(factura_id)

            # Abrir diálogo de impresión
            dialog = InvoicePrintDialog(
                numero_factura=numero_factura,
                fecha=fecha,
                cliente=cliente,
                forma_pago=factura.forma_pago,
                total_usd=factura.total,
                total_ves=factura.total_ves,
                items=items,
                parent=self,
            )
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al preparar impresión: {e}")

    # ==========================================
    # TAB: VENTAS
    # ==========================================

    def crear_tab_ventas(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filtros
        filtros_group = QGroupBox("Filtros de Período")
        filtros_layout = QHBoxLayout(filtros_group)

        filtros_layout.addWidget(QLabel("Desde:"))
        self.date_ventas_inicio = QDateEdit()
        self.date_ventas_inicio.setCalendarPopup(True)
        self.date_ventas_inicio.setDate(QDate.currentDate().addDays(-30))  # Último mes
        self.date_ventas_inicio.setStyleSheet(
            """
                QDateEdit {
                    background-color: #f9f9f9;   /* color de fondo */
                    color: black;                  /* color del texto */
                    border: 1px solid gray;        /* borde */
                    border-radius: 4px;            /* esquinas redondeadas */
                    padding: 2px;                  /* espacio interno */
                }
            """
        )
        filtros_layout.addWidget(self.date_ventas_inicio)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.date_ventas_fin = QDateEdit()
        self.date_ventas_fin.setCalendarPopup(True)
        self.date_ventas_fin.setDate(QDate.currentDate())
        self.date_ventas_fin.setStyleSheet(
            """
                QDateEdit {
                    background-color: #f9f9f9;   /* color de fondo */
                    color: black;                  /* color del texto */
                    border: 1px solid gray;        /* borde */
                    border-radius: 4px;            /* esquinas redondeadas */
                    padding: 2px;                  /* espacio interno */
                }
            """
        )

        filtros_layout.addWidget(self.date_ventas_fin)

        btn_consultar_ventas = QPushButton("Consultar")
        btn_consultar_ventas.clicked.connect(self.cargar_ventas)
        filtros_layout.addWidget(btn_consultar_ventas)

        filtros_layout.addStretch()
        layout.addWidget(filtros_group)

        # Métricas
        metricas_frame = QFrame()
        metricas_frame.setObjectName("ventasMetricasFrame")
        metricas_layout = QHBoxLayout(metricas_frame)

        self.label_total_usd = QLabel("Total USD: $0.00")
        self.label_total_usd.setFont(QFont("Segoe UI", 14, QFont.Bold))
        metricas_layout.addWidget(self.label_total_usd)

        self.label_total_ves = QLabel("Total VES: 0.00 Bs")
        self.label_total_ves.setFont(QFont("Segoe UI", 14, QFont.Bold))
        metricas_layout.addWidget(self.label_total_ves)

        self.label_num_ordenes = QLabel("Órdenes: 0")
        self.label_num_ordenes.setFont(QFont("Segoe UI", 14, QFont.Bold))
        metricas_layout.addWidget(self.label_num_ordenes)

        self.label_ticket_promedio = QLabel("Ticket Prom: $0.00")
        self.label_ticket_promedio.setFont(QFont("Segoe UI", 14, QFont.Bold))
        metricas_layout.addWidget(self.label_ticket_promedio)

        layout.addWidget(metricas_frame)

        # Tabla de ventas diarias
        layout.addWidget(QLabel("Ventas Diarias:"))
        self.table_ventas = QTableWidget(0, 3)
        self.table_ventas.setHorizontalHeaderLabels(["Fecha", "Total (USD)", "Órdenes"])
        self.table_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_ventas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_ventas.setAlternatingRowColors(True)
        layout.addWidget(self.table_ventas)

        # Cargar datos iniciales
        self.cargar_ventas()

        return tab

    def cargar_ventas(self):
        fecha_inicio = self.date_ventas_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.date_ventas_fin.date().toString("yyyy-MM-dd")

        # Obtener métricas
        total_usd, total_ves, num_ordenes, ticket_promedio = (
            reportes_service.obtener_ventas_por_periodo(fecha_inicio, fecha_fin)
        )

        # Actualizar labels
        self.label_total_usd.setText(f"Total USD: ${total_usd:,.2f}")
        self.label_total_ves.setText(f"Total VES: {total_ves:,.2f} Bs")
        self.label_num_ordenes.setText(f"Órdenes: {num_ordenes}")
        self.label_ticket_promedio.setText(f"Ticket Prom: ${ticket_promedio:,.2f}")

        # Obtener ventas diarias
        ventas_diarias = reportes_service.obtener_ventas_diarias(
            fecha_inicio, fecha_fin
        )

        # Llenar tabla
        self.table_ventas.setRowCount(0)
        for fecha, total, ordenes in ventas_diarias:
            ridx = self.table_ventas.rowCount()
            self.table_ventas.insertRow(ridx)

            self.table_ventas.setItem(ridx, 0, QTableWidgetItem(fecha))
            self.table_ventas.setItem(ridx, 1, QTableWidgetItem(f"${total:,.2f}"))
            self.table_ventas.setItem(ridx, 2, QTableWidgetItem(str(ordenes)))

    # ==========================================
    # TAB: PRODUCTOS
    # ==========================================

    def crear_tab_productos(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filtros
        filtros_group = QGroupBox("Filtros de Período")
        filtros_layout = QHBoxLayout(filtros_group)

        filtros_layout.addWidget(QLabel("Desde:"))
        self.date_productos_inicio = QDateEdit()
        self.date_productos_inicio.setCalendarPopup(True)
        self.date_productos_inicio.setDate(QDate.currentDate().addDays(-30))
        self.date_productos_inicio.setStyleSheet(
            """
                QDateEdit {
                    background-color: #f9f9f9;   /* color de fondo */
                    color: black;                  /* color del texto */
                    border: 1px solid gray;        /* borde */
                    border-radius: 4px;            /* esquinas redondeadas */
                    padding: 2px;                  /* espacio interno */
                }
            """
        )
        filtros_layout.addWidget(self.date_productos_inicio)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.date_productos_fin = QDateEdit()
        self.date_productos_fin.setCalendarPopup(True)
        self.date_productos_fin.setDate(QDate.currentDate())
        self.date_productos_fin.setStyleSheet(
            """
                QDateEdit {
                    background-color: #f9f9f9;   /* color de fondo */
                    color: black;                  /* color del texto */
                    border: 1px solid gray;        /* borde */
                    border-radius: 4px;            /* esquinas redondeadas */
                    padding: 2px;                  /* espacio interno */
                }
            """
        )
        filtros_layout.addWidget(self.date_productos_fin)

        btn_consultar_productos = QPushButton("Consultar")
        btn_consultar_productos.clicked.connect(self.cargar_productos)
        filtros_layout.addWidget(btn_consultar_productos)

        filtros_layout.addStretch()
        layout.addWidget(filtros_group)

        # Top por Cantidad
        layout.addWidget(QLabel("Top 10 Productos por Cantidad Vendida:"))
        self.table_top_cantidad = QTableWidget(0, 4)
        self.table_top_cantidad.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Ingresos", "% Total"]
        )
        self.table_top_cantidad.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table_top_cantidad.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_top_cantidad.setAlternatingRowColors(True)
        layout.addWidget(self.table_top_cantidad)

        # Top por Ingresos
        layout.addWidget(QLabel("Top 10 Productos por Ingresos:"))
        self.table_top_ingresos = QTableWidget(0, 4)
        self.table_top_ingresos.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Ingresos", "% Total"]
        )
        self.table_top_ingresos.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table_top_ingresos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_top_ingresos.setAlternatingRowColors(True)
        layout.addWidget(self.table_top_ingresos)

        # Cargar datos iniciales
        self.cargar_productos()

        return tab

    def cargar_productos(self):
        fecha_inicio = self.date_productos_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.date_productos_fin.date().toString("yyyy-MM-dd")

        # Calcular total de ingresos para porcentajes
        total_ingresos = reportes_service.calcular_total_ingresos(
            fecha_inicio, fecha_fin
        )

        # Top por cantidad
        top_cantidad = reportes_service.obtener_productos_mas_vendidos(
            fecha_inicio, fecha_fin, 10
        )
        self.table_top_cantidad.setRowCount(0)
        for producto, cantidad, ingresos in top_cantidad:
            ridx = self.table_top_cantidad.rowCount()
            self.table_top_cantidad.insertRow(ridx)

            porcentaje = reportes_service.calcular_porcentaje(ingresos, total_ingresos)

            self.table_top_cantidad.setItem(ridx, 0, QTableWidgetItem(producto))
            self.table_top_cantidad.setItem(
                ridx, 1, QTableWidgetItem(str(int(cantidad)))
            )
            self.table_top_cantidad.setItem(
                ridx, 2, QTableWidgetItem(f"${ingresos:,.2f}")
            )
            self.table_top_cantidad.setItem(
                ridx, 3, QTableWidgetItem(f"{porcentaje:.1f}%")
            )

        # Top por ingresos
        top_ingresos = reportes_service.obtener_productos_por_ingresos(
            fecha_inicio, fecha_fin, 10
        )
        self.table_top_ingresos.setRowCount(0)
        for producto, cantidad, ingresos in top_ingresos:
            ridx = self.table_top_ingresos.rowCount()
            self.table_top_ingresos.insertRow(ridx)

            porcentaje = reportes_service.calcular_porcentaje(ingresos, total_ingresos)

            self.table_top_ingresos.setItem(ridx, 0, QTableWidgetItem(producto))
            self.table_top_ingresos.setItem(
                ridx, 1, QTableWidgetItem(str(int(cantidad)))
            )
            self.table_top_ingresos.setItem(
                ridx, 2, QTableWidgetItem(f"${ingresos:,.2f}")
            )
            self.table_top_ingresos.setItem(
                ridx, 3, QTableWidgetItem(f"{porcentaje:.1f}%")
            )
