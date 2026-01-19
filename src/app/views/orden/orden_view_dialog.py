import logging

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services import orden_service
from ...services import tasa_cambio_service

logger = logging.getLogger(__name__)


class OrdenViewDialog(QDialog):
    """
    Diálogo de solo lectura para ver los detalles de una orden.
    No permite agregar, eliminar o modificar items.
    """

    def __init__(self, orden_id: int, parent=None):
        super().__init__(parent)
        self.orden_id = orden_id
        self.orden = None
        self.detalles = []

        self.setWindowTitle("Ver Orden (Solo Lectura)")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        """Construye la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("Detalles de la Orden")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Frame de información
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(8)

        self.label_mesa = QLabel()
        self.label_mesa.setFont(QFont("Segoe UI", 11))
        info_layout.addWidget(self.label_mesa)

        self.label_cliente = QLabel()
        self.label_cliente.setFont(QFont("Segoe UI", 11))
        info_layout.addWidget(self.label_cliente)

        self.label_fecha = QLabel()
        self.label_fecha.setFont(QFont("Segoe UI", 10))
        info_layout.addWidget(self.label_fecha)

        self.label_estado = QLabel()
        self.label_estado.setFont(QFont("Segoe UI", 10, QFont.Bold))
        info_layout.addWidget(self.label_estado)

        layout.addWidget(info_frame)

        # Tabla de items
        items_label = QLabel("Items de la Orden:")
        items_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(items_label)

        self.tabla_items = QTableWidget()
        self.tabla_items.setColumnCount(4)
        self.tabla_items.setHorizontalHeaderLabels(
            ["Producto", "Precio Unit.", "Cantidad", "Subtotal"]
        )
        self.tabla_items.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_items.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        self.tabla_items.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self.tabla_items.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )
        self.tabla_items.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_items.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_items.setAlternatingRowColors(True)
        layout.addWidget(self.tabla_items)

        # Totales
        totales_layout = QHBoxLayout()
        totales_layout.addStretch()

        totales_frame = QFrame()
        totales_frame.setFrameShape(QFrame.StyledPanel)
        totales_inner = QVBoxLayout(totales_frame)
        totales_inner.setContentsMargins(15, 10, 15, 10)
        totales_inner.setSpacing(5)

        self.label_total_usd = QLabel()
        self.label_total_usd.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.label_total_usd.setAlignment(Qt.AlignRight)
        totales_inner.addWidget(self.label_total_usd)

        self.label_total_ves = QLabel()
        self.label_total_ves.setFont(QFont("Segoe UI", 10))
        self.label_total_ves.setAlignment(Qt.AlignRight)
        totales_inner.addWidget(self.label_total_ves)

        totales_layout.addWidget(totales_frame)
        layout.addLayout(totales_layout)

        # Botón Cerrar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumWidth(120)
        btn_cerrar.setMinimumHeight(35)
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

    def cargar_datos(self):
        """Carga los datos de la orden y los muestra"""
        try:
            # Obtener orden (devuelve dict)
            self.orden = orden_service.obtener_orden_por_id(self.orden_id)
            if not self.orden:
                logger.error(f"No se encontró la orden {self.orden_id}")
                self.label_mesa.setText("Error: Orden no encontrada")
                return

            # Obtener detalles (devuelve lista de tuplas)
            self.detalles = orden_service.obtener_detalles_orden(self.orden_id)

            # Mostrar información de la orden
            self.label_mesa.setText(f"Mesa: {self.orden['mesa_id']}")
            self.label_cliente.setText(f"Cliente: {self.orden.get('cliente', 'N/A')}")
            self.label_fecha.setText(f"Fecha: {self.orden.get('fecha', 'N/A')}")
            self.label_estado.setText(
                f"Estado: {self.orden.get('estado', 'N/A').upper()}"
            )

            # Llenar tabla de items
            # Formato tupla: (detalle_id, item_id, nombre, cantidad,
            #                 precio_unitario, subtotal, variant_id)
            self.tabla_items.setRowCount(len(self.detalles))
            for row, detalle in enumerate(self.detalles):
                (
                    detalle_id,
                    item_id,
                    nombre,
                    cantidad,
                    precio_unit,
                    subtotal,
                    variant_id,
                ) = detalle

                # Producto (nombre)
                item_producto = QTableWidgetItem(nombre or "N/A")
                item_producto.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.tabla_items.setItem(row, 0, item_producto)

                # Precio unitario
                precio_unit = float(precio_unit or 0.0)
                item_precio = QTableWidgetItem(f"${precio_unit:.2f}")
                item_precio.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla_items.setItem(row, 1, item_precio)

                # Cantidad
                item_cantidad = QTableWidgetItem(str(int(cantidad)))
                item_cantidad.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.tabla_items.setItem(row, 2, item_cantidad)

                # Subtotal
                subtotal = float(subtotal or 0.0)
                item_subtotal = QTableWidgetItem(f"${subtotal:.2f}")
                item_subtotal.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla_items.setItem(row, 3, item_subtotal)

            # Mostrar totales
            total_usd = float(self.orden.get("total", 0.0))
            self.label_total_usd.setText(f"Total: ${total_usd:.2f} USD")

            # Calcular equivalente en VES
            try:
                tasa = tasa_cambio_service.obtener_tasa_actual()
                if tasa:
                    total_ves = total_usd * tasa.tasa
                    self.label_total_ves.setText(
                        f"Equivalente: Bs. {total_ves:,.2f} VES"
                    )
                else:
                    self.label_total_ves.setText("(Tasa de cambio no disponible)")
            except Exception as e:
                logger.warning(f"No se pudo calcular equivalente en VES: {e}")
                self.label_total_ves.setText("")

        except Exception as e:
            logger.exception(f"Error al cargar datos de la orden: {e}")
            self.label_mesa.setText(f"Error al cargar orden: {e}")
