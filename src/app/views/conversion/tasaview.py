from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFrame,
    QDoubleSpinBox,
    QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import datetime
from ...services import tasa_cambio_service
from ...models import TasaCambio


class TasaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Tasa de Cambio USD ↔ VES")
        self.resize(700, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ===== TASA ACTUAL (Prominente) =====
        self.frame_tasa_actual = QFrame()
        self.frame_tasa_actual.setObjectName("tasaActualFrame")
        frame_layout = QVBoxLayout(self.frame_tasa_actual)

        self.label_tasa_actual = QLabel("1 USD = -- Bs")
        self.label_tasa_actual.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.label_tasa_actual.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.label_tasa_actual)

        self.label_fecha_actualizacion = QLabel("Sin tasa registrada")
        self.label_fecha_actualizacion.setFont(QFont("Segoe UI", 10))
        self.label_fecha_actualizacion.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.label_fecha_actualizacion)

        main_layout.addWidget(self.frame_tasa_actual)

        # ===== ACTUALIZAR TASA =====
        group_actualizar = QGroupBox("Actualizar Tasa del Día")
        group_actualizar_layout = QHBoxLayout(group_actualizar)

        group_actualizar_layout.addWidget(QLabel("Nueva tasa:"))

        self.input_tasa = QDoubleSpinBox()
        self.input_tasa.setMinimum(0.01)
        self.input_tasa.setMaximum(999999.99)
        self.input_tasa.setDecimals(2)
        self.input_tasa.setSingleStep(0.10)
        self.input_tasa.setSuffix(" Bs/USD")
        self.input_tasa.setMinimumWidth(150)
        group_actualizar_layout.addWidget(self.input_tasa)

        btn_guardar = QPushButton("Guardar Tasa")
        btn_guardar.setMinimumHeight(35)
        btn_guardar.clicked.connect(self.guardar_tasa)
        group_actualizar_layout.addWidget(btn_guardar)

        group_actualizar_layout.addStretch()
        main_layout.addWidget(group_actualizar)

        # ===== CONVERTIDOR BIDIRECCIONAL =====
        group_convertidor = QGroupBox("Convertidor de Moneda")
        conv_layout = QVBoxLayout(group_convertidor)

        # USD → VES
        usd_layout = QHBoxLayout()
        usd_layout.addWidget(QLabel("USD:"))

        self.input_usd = QDoubleSpinBox()
        self.input_usd.setMinimum(0.00)
        self.input_usd.setMaximum(999999.99)
        self.input_usd.setDecimals(2)
        self.input_usd.setPrefix("$ ")
        self.input_usd.setMinimumWidth(150)
        self.input_usd.valueChanged.connect(self.convertir_usd_a_ves)
        usd_layout.addWidget(self.input_usd)

        usd_layout.addWidget(QLabel("→"))

        self.label_resultado_ves = QLabel("0.00 Bs")
        self.label_resultado_ves.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.label_resultado_ves.setMinimumWidth(150)
        usd_layout.addWidget(self.label_resultado_ves)

        usd_layout.addStretch()
        conv_layout.addLayout(usd_layout)

        # VES → USD
        ves_layout = QHBoxLayout()
        ves_layout.addWidget(QLabel("VES:"))

        self.input_ves = QDoubleSpinBox()
        self.input_ves.setMinimum(0.00)
        self.input_ves.setMaximum(99999999.99)
        self.input_ves.setDecimals(2)
        self.input_ves.setSuffix(" Bs")
        self.input_ves.setMinimumWidth(150)
        self.input_ves.valueChanged.connect(self.convertir_ves_a_usd)
        ves_layout.addWidget(self.input_ves)

        ves_layout.addWidget(QLabel("→"))

        self.label_resultado_usd = QLabel("$ 0.00")
        self.label_resultado_usd.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.label_resultado_usd.setMinimumWidth(150)
        ves_layout.addWidget(self.label_resultado_usd)

        ves_layout.addStretch()
        conv_layout.addLayout(ves_layout)

        main_layout.addWidget(group_convertidor)

        # ===== HISTORIAL =====
        group_historial = QGroupBox("Historial de Tasas")
        hist_layout = QVBoxLayout(group_historial)

        self.tabla = QTableWidget(0, 4)
        self.tabla.setHorizontalHeaderLabels(
            ["Fecha", "Tasa (Bs/USD)", "Variación (%)", "Diferencia"]
        )
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        hist_layout.addWidget(self.tabla)

        main_layout.addWidget(group_historial)

        # Cargar datos iniciales
        self.cargar_historial()
        self.actualizar_tasa_actual()

    def actualizar_tasa_actual(self):
        """Actualiza el display de la tasa actual"""
        tasa_obj = tasa_cambio_service.obtener_tasa_del_dia()
        if tasa_obj:
            self.label_tasa_actual.setText(f"1 USD = {tasa_obj.tasa:.2f} Bs")
            self.label_fecha_actualizacion.setText(
                f"Última actualización: {tasa_obj.fecha}"
            )
            self.input_tasa.setValue(tasa_obj.tasa)
        else:
            self.label_tasa_actual.setText("1 USD = -- Bs")
            self.label_fecha_actualizacion.setText("Sin tasa registrada")

    def guardar_tasa(self):
        """Guarda la nueva tasa del día"""
        tasa = self.input_tasa.value()

        if tasa <= 0:
            QMessageBox.warning(self, "Error", "La tasa debe ser mayor a 0")
            return

        fecha = datetime.date.today().isoformat()

        # Verificar cambio significativo
        tasa_anterior = tasa_cambio_service.obtener_tasa_del_dia()
        if tasa_anterior:
            variacion = abs((tasa - tasa_anterior.tasa) / tasa_anterior.tasa) * 100
            if variacion > 5:
                reply = QMessageBox.question(
                    self,
                    "Cambio Significativo",
                    f"La tasa ha variado {variacion:.1f}% respecto al día anterior.\n"
                    f"¿Desea continuar?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

        ok, error = tasa_cambio_service.guardar_tasa(fecha, tasa)

        if ok:
            QMessageBox.information(
                self, "Éxito", f"Tasa guardada: {tasa:.2f} Bs/USD para {fecha}"
            )
            self.cargar_historial()
            self.actualizar_tasa_actual()
            # Actualizar conversiones
            self.convertir_usd_a_ves(self.input_usd.value())
            self.convertir_ves_a_usd(self.input_ves.value())
        else:
            QMessageBox.warning(self, "Error", error or "No se pudo guardar la tasa")

    def convertir_usd_a_ves(self, valor):
        """Convierte USD a VES en tiempo real"""
        tasa_obj = tasa_cambio_service.obtener_tasa_del_dia()
        if tasa_obj and valor > 0:
            resultado = valor * tasa_obj.tasa
            self.label_resultado_ves.setText(f"{resultado:,.2f} Bs")
        else:
            self.label_resultado_ves.setText("0.00 Bs")

    def convertir_ves_a_usd(self, valor):
        """Convierte VES a USD en tiempo real"""
        tasa_obj = tasa_cambio_service.obtener_tasa_del_dia()
        if tasa_obj and tasa_obj.tasa > 0 and valor > 0:
            resultado = valor / tasa_obj.tasa
            self.label_resultado_usd.setText(f"$ {resultado:,.2f}")
        else:
            self.label_resultado_usd.setText("$ 0.00")

    def cargar_historial(self):
        """Carga el historial de tasas con cálculo de variación"""
        tasas = tasa_cambio_service.listar_tasas()
        self.tabla.setRowCount(0)

        for i, tasa in enumerate(tasas):
            self.tabla.insertRow(i)

            # Fecha
            item_fecha = QTableWidgetItem(tasa.fecha)
            item_fecha.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 0, item_fecha)

            # Tasa
            item_tasa = QTableWidgetItem(tasa.get_tasa_formateada())
            item_tasa.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 1, item_tasa)

            # Calcular variación con el día anterior
            if i < len(tasas) - 1:
                tasa_anterior = tasas[i + 1].tasa
                variacion = ((tasa.tasa - tasa_anterior) / tasa_anterior) * 100
                diferencia = tasa.tasa - tasa_anterior

                # Variación %
                item_variacion = QTableWidgetItem(f"{variacion:+.2f}%")
                item_variacion.setTextAlignment(Qt.AlignCenter)
                if variacion > 0:
                    item_variacion.setForeground(QColor("#27ae60"))  # Verde
                elif variacion < 0:
                    item_variacion.setForeground(QColor("#e74c3c"))  # Rojo
                self.tabla.setItem(i, 2, item_variacion)

                # Diferencia
                item_diferencia = QTableWidgetItem(f"{diferencia:+.2f}")
                item_diferencia.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if diferencia > 0:
                    item_diferencia.setForeground(QColor("#27ae60"))
                elif diferencia < 0:
                    item_diferencia.setForeground(QColor("#e74c3c"))
                self.tabla.setItem(i, 3, item_diferencia)
            else:
                # Primera tasa, sin variación
                item_variacion = QTableWidgetItem("--")
                item_variacion.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(i, 2, item_variacion)

                item_diferencia = QTableWidgetItem("--")
                item_diferencia.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(i, 3, item_diferencia)

        self.tabla.resizeColumnsToContents()
