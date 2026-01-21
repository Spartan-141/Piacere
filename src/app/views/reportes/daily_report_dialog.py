from datetime import datetime, date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QMarginsF
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
from PySide6.QtPrintSupport import QPrinter

from ...services import reportes_service, tasa_cambio_service
from ...utils.invoice_html_generator import generate_invoice_html


class DailyReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reporte de Cierre de Caja")
        self.setMinimumSize(600, 750)
        
        self.fecha_str = date.today().isoformat()
        self.report_html = ""
        
        self.load_data_and_build_ui()

    def load_data_and_build_ui(self):
        # 1. Obtener datos
        try:
            data = reportes_service.obtener_resumen_ventas_dia(self.fecha_str)
            
            # Obtener tasa actual para referencia
            tasa_obj = tasa_cambio_service.obtener_tasa(self.fecha_str)
            tasa_valor = tasa_obj.tasa if tasa_obj else 0.0
            
            # 2. Mapear a formato de "Factura"
            # Cliente -> "ADMINISTRADOR / SISTEMA"
            # Forma de Pago -> "N/A"
            # Items -> Los desgloses por método de pago
            
            items_mapped = []
            for d in data["desglose"]:
                # d = {'metodo': 'Efectivo', 'cantidad': 5, 'usd': 100.0, 'ves': ...}
                items_mapped.append({
                    "producto": f"Ventas: {d['metodo']}",
                    "variante": f"En Bs: {d['ves']:,.2f}",
                    "cantidad": d['cantidad'],
                    "precio": 0, # No aplica precio unitario real, o podríamos poner promedio
                    "subtotal": d['usd'] # El subtotal es el total USD de ese método
                })
                
            # Agregar info de tasa como un item informativo o en notas?
            # Mejor lo agregamos como cliente o variante
            
            total_usd = data["total_usd"]
            total_ves = data["total_ves"]
            num_ordenes = data["total_ordenes"]
            
            # Generar HTML reusando el generador de facturas
            # Manipulamos strings para que se vea como reporte
            
            html = generate_invoice_html(
                numero_factura=f"CIERRE-{self.fecha_str.replace('-', '')}",
                fecha=datetime.now(),
                cliente=f"CIERRE DIARIO (Tasa: {tasa_valor:,.2f} Bs)",
                forma_pago="Múltiple",
                total_usd=total_usd,
                total_ves=total_ves,
                items=items_mapped
            )
            
            # Inyectar un título personalizado reemplazando el estándar si es necesario, 
            # pero "FACTURA DE VENTA" tal vez no cuadre. 
            # El generador es rígido. Por ahora lo dejamos así y el sistema "hackea" el look.
            # O mejor, hacemos un pequeño replace en el HTML resultante.
            html = html.replace("FACTURA DE VENTA", "REPORTE DE CIERRE DIARIO")
            html = html.replace("Cliente:", "Reporte para:")
            html = html.replace("Factura #:", "Ref. Cierre:")
            
            self.report_html = html
            
            # 3. Construir UI
            layout = QVBoxLayout(self)
            
            preview = QTextEdit()
            preview.setReadOnly(True)
            preview.setStyleSheet("background-color: #ffffff; color: black")
            preview.setHtml(self.report_html)
            layout.addWidget(preview)
            
            btn_layout = QHBoxLayout()
            
            btn_pdf = QPushButton("💾 Guardar PDF")
            btn_pdf.clicked.connect(self.export_pdf)
            btn_pdf.setStyleSheet("background-color: #2980b9; color: white; padding: 8px;")
            
            btn_close = QPushButton("Cerrar")
            btn_close.clicked.connect(self.accept)
            
            btn_layout.addStretch()
            btn_layout.addWidget(btn_pdf)
            btn_layout.addWidget(btn_close)
            
            layout.addLayout(btn_layout)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte: {e}")
            import traceback
            traceback.print_exc()

    def export_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Cierre como PDF",
            f"Cierre_{self.fecha_str}.pdf",
            "PDF Files (*.pdf)",
        )

        if filename:
            try:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(filename)
                printer.setPageSize(QPageSize(QPageSize.Letter))
                printer.setPageOrientation(QPageLayout.Orientation.Portrait)
                printer.setPageMargins(
                    QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter
                )

                document = QTextDocument()
                document.setHtml(self.report_html)
                document.print_(printer)

                QMessageBox.information(
                    self, "PDF Guardado", f"Reporte guardado exitosamente."
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error guardando PDF: {e}")
