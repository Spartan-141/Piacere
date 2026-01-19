"""
Diálogo para mostrar listados de órdenes (búsqueda y listado completo)
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class OrdenesDialog(QDialog):
    """Diálogo para mostrar resultados de búsqueda de órdenes"""

    def __init__(self, ordenes_data, parent=None):
        super().__init__(parent)
        self.ordenes_data = ordenes_data
        self.setWindowTitle("Órdenes")
        self.setMinimumSize(700, 400)
        self.setModal(True)

        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        titulo = QLabel(f"Órdenes Encontradas ({len(self.ordenes_data)})")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["Cliente", "Mesa", "Total (USD)", "Estado"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.doubleClicked.connect(self.ver_detalle_orden)
        layout.addWidget(self.tabla)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_ver = QPushButton("Ver Detalles")
        btn_ver.setMinimumWidth(120)
        btn_ver.setMinimumHeight(35)
        btn_ver.clicked.connect(self.ver_detalle_orden)
        btn_layout.addWidget(btn_ver)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumWidth(120)
        btn_cerrar.setMinimumHeight(35)
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

    def cargar_datos(self):
        """Carga los datos de órdenes en la tabla"""
        self.tabla.setRowCount(len(self.ordenes_data))

        for row, orden in enumerate(self.ordenes_data):
            # orden = (id, cliente_nombre, total, estado, mesa_numero)
            orden_id, cliente, total, estado, mesa = orden

            # Cliente
            item_cliente = QTableWidgetItem(cliente or "N/A")
            item_cliente.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_cliente.setData(Qt.UserRole, orden_id)  # Guardar ID
            self.tabla.setItem(row, 0, item_cliente)

            # Mesa
            item_mesa = QTableWidgetItem(str(mesa))
            item_mesa.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tabla.setItem(row, 1, item_mesa)

            # Total
            total_val = float(total or 0.0)
            item_total = QTableWidgetItem(f"${total_val:.2f}")
            item_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 2, item_total)

            # Estado
            item_estado = QTableWidgetItem(estado.upper())
            item_estado.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.tabla.setItem(row, 3, item_estado)

    def ver_detalle_orden(self):
        """Abre el diálogo de vista de orden"""
        row = self.tabla.currentRow()
        if row < 0:
            return

        # Obtener ID de la orden
        orden_id = self.tabla.item(row, 0).data(Qt.UserRole)

        # Abrir diálogo de vista de orden
        from ..orden.orden_view_dialog import OrdenViewDialog

        dialog = OrdenViewDialog(orden_id, parent=self)
        dialog.exec()
