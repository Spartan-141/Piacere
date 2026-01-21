from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QDoubleSpinBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services import tasa_cambio_service

class RateUpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Actualizar Tasa del Día")
        self.setFixedSize(350, 250)
        self.fecha_hoy = date.today().isoformat()
        self.setup_ui()
        self.load_current_rate()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        lbl_titulo = QLabel("Tasa de Cambio (BCV/Paralelo)")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(lbl_titulo)

        # Muestra la fecha
        lbl_fecha = QLabel(f"Fecha: {self.fecha_hoy}")
        lbl_fecha.setAlignment(Qt.AlignCenter)
        lbl_fecha.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(lbl_fecha)

        # Input
        self.spin_tasa = QDoubleSpinBox()
        self.spin_tasa.setPrefix("Bs. ")
        self.spin_tasa.setDecimals(2)
        self.spin_tasa.setRange(0.01, 10000.00)
        self.spin_tasa.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 24px;
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        self.spin_tasa.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.spin_tasa)

        # Botones
        btn_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        btn_guardar = QPushButton("Guardar Tasa")
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        btn_guardar.clicked.connect(self.guardar_tasa)

        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_guardar)
        
        layout.addLayout(btn_layout)

    def load_current_rate(self):
        tasa = tasa_cambio_service.obtener_tasa(self.fecha_hoy)
        if tasa:
            self.spin_tasa.setValue(tasa.tasa)
        else:
            # Intentar obtener la última tasa registrada como referencia
            ultima = tasa_cambio_service.obtener_tasa_del_dia()
            if ultima:
                self.spin_tasa.setValue(ultima.tasa)

    def guardar_tasa(self):
        valor = self.spin_tasa.value()
        ok, err = tasa_cambio_service.guardar_tasa(self.fecha_hoy, valor)
        
        if ok:
            QMessageBox.information(self, "Éxito", "Tasa actualizada correctamente")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la tasa: {err}")
