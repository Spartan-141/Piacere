# src/app/views/reportes/invoice_print_dialog.py
from typing import List, Tuple
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import Qt, QMarginsF
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog


class InvoicePrintDialog(QDialog):
    """
    Diálogo para imprimir o exportar facturas como PDF.
    """

    def __init__(
        self,
        numero_factura: str,
        fecha: str,
        cliente: str,
        forma_pago: str,
        total_usd: float,
        total_ves: float,
        items: List[Tuple],
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Imprimir Factura {numero_factura}")
        self.setMinimumSize(600, 700)

        self.numero_factura = numero_factura
        self.fecha = fecha
        self.cliente = cliente
        self.forma_pago = forma_pago
        self.total_usd = total_usd
        self.total_ves = total_ves
        self.items = items

        self._setup_ui()
        self._generate_invoice_html()

    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)

        # Vista previa del documento
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("background-color: #ffffff; color: black")
        layout.addWidget(self.preview)

        # Botones
        button_layout = QHBoxLayout()

        btn_print = QPushButton("🖨️ Imprimir")
        btn_print.clicked.connect(self._print_invoice)

        btn_pdf = QPushButton("📄 Guardar PDF")
        btn_pdf.clicked.connect(self._save_as_pdf)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.reject)

        button_layout.addWidget(btn_print)
        button_layout.addWidget(btn_pdf)
        button_layout.addStretch()
        button_layout.addWidget(btn_close)

        layout.addLayout(button_layout)

    def _generate_invoice_html(self):
        """Genera el HTML de la factura con formato profesional"""
        # Parsear fecha
        try:
            if isinstance(self.fecha, str):
                fecha_obj = datetime.fromisoformat(self.fecha.replace(" ", "T"))
                fecha_formatted = fecha_obj.strftime("%d/%m/%Y %I:%M %p")
            else:
                fecha_formatted = self.fecha.strftime("%d/%m/%Y %I:%M %p")
        except Exception:
            fecha_formatted = str(self.fecha)

        # Construir tabla de items
        items_html = []
        for item in self.items:
            producto = item[0] or "Producto"
            variante = item[1] or ""
            cantidad = item[2]
            precio_unit = item[3]
            subtotal = item[4]

            nombre_completo = f"{producto}"
            if variante:
                nombre_completo += f" ({variante})"

            items_html.append(
                f"""
                <tr>
                    <td style='padding: 4px 8px; border-bottom: 1px solid #eee;'>{nombre_completo}</td>
                    <td style='padding: 4px 8px; text-align: center; border-bottom: 1px solid #eee;'>{cantidad}</td>
                    <td style='padding: 4px 8px; text-align: right; border-bottom: 1px solid #eee;'>${precio_unit:.2f}</td>
                    <td style='padding: 4px 8px; text-align: right; border-bottom: 1px solid #eee;'>${subtotal:.2f}</td>
                </tr>
            """
            )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    margin: 20px;
                    font-size: 12pt;
                }}
                .invoice-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    border: 2px solid #333;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #333;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24pt;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 5px 0;
                    font-size: 10pt;
                }}
                .meta {{
                    margin-bottom: 20px;
                    border-bottom: 1px dashed #666;
                    padding-bottom: 10px;
                }}
                .meta-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 5px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background-color: #f0f0f0;
                    padding: 8px;
                    text-align: left;
                    border-bottom: 2px solid #333;
                    font-weight: bold;
                }}
                .totals {{
                    margin-top: 20px;
                    border-top: 2px solid #333;
                    padding-top: 10px;
                }}
                .total-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 8px 0;
                    font-size: 11pt;
                }}
                .total-row.grand {{
                    font-size: 14pt;
                    font-weight: bold;
                    border-top: 2px solid #333;
                    padding-top: 10px;
                    margin-top: 10px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px dashed #666;
                    font-size: 10pt;
                }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <!-- Header -->
                <div class="header">
                    <h1>PIACERE</h1>
                    <p>Calle No definida</p>
                    <p>Tel: No definido</p>
                    <p style="margin-top: 10px; font-weight: bold;">FACTURA DE VENTA</p>
                </div>
                
                <!-- Meta Information -->
                <div class="meta">
                    <div class="meta-row">
                        <span><strong>Factura #:</strong> {self.numero_factura}</span>    
                    </div>
                    <div class="meta-row">   
                        <span><strong>Fecha:</strong> {fecha_formatted}</span>
                    </div>
                    <div class="meta-row">
                        <span><strong>Cliente:</strong> {self.cliente}</span>
                    </div>
                    <div class="meta-row">
                        <span><strong>Forma de Pago:</strong> {self.forma_pago}</span>
                    </div>

                </div>
                
                <!-- Items Table -->
                <table>
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th style="text-align: center; width: 80px;">Cant.</th>
                            <th style="text-align: right; width: 100px;">Precio Unit.</th>
                            <th style="text-align: right; width: 100px;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(items_html)}
                    </tbody>
                </table>
                
                <!-- Totals -->
                <div class="totals">
                    <div class="total-row">
                        <span>Subtotal:</span>
                        <span>${self.total_usd:.2f}</span>
                    </div>
                    <div class="total-row grand">
                        <span>TOTAL USD:</span>
                        <span>${self.total_usd:.2f}</span>
                    </div>
                    <div class="total-row">
                        <span>TOTAL Bs:</span>
                        <span>{self.total_ves:,.2f} Bs</span>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <p><strong>¡Gracias por su compra!</strong></p>
                </div>
            </div>
        </body>
        </html>
        """

        self.preview.setHtml(html)
        self.invoice_html = html

    def _print_invoice(self):
        """Imprime la factura usando el diálogo de impresión del sistema"""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.Letter))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.Accepted:
            document = QTextDocument()
            document.setHtml(self.invoice_html)
            document.print_(printer)
            QMessageBox.information(
                self,
                "Impresión Exitosa",
                f"Factura {self.numero_factura} enviada a impresora",
            )

    def _save_as_pdf(self):
        """Guarda la factura como archivo PDF"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Factura como PDF",
            f"Factura_{self.numero_factura}.pdf",
            "PDF Files (*.pdf)",
        )

        if filename:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            printer.setPageSize(QPageSize(QPageSize.Letter))
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)
            printer.setPageMargins(
                QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter
            )

            document = QTextDocument()
            document.setHtml(self.invoice_html)
            document.print_(printer)

            QMessageBox.information(
                self, "PDF Guardado", f"Factura guardada como:\n{filename}"
            )

    def _handle_paint_request(self, printer):
        """Maneja la solicitud de pintado para la vista previa"""
        document = QTextDocument()
        document.setHtml(self.invoice_html)
        document.print_(printer)
