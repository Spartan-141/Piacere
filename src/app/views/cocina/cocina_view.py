# src/app/views/cocina/cocina_view.py
"""
Vista de Cocina para el rol Cocinero
Muestra órdenes en preparación con posibilidad de marcar como listo
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ...services import cocina_service


class OrdenCard(QFrame):
    """Widget que representa una orden en la vista de cocina"""
    
    def __init__(self, orden_data: dict, parent_view):
        super().__init__()
        self.orden_data = orden_data
        self.parent_view = parent_view
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("ordenCard")
        self.setFrameShape(QFrame.StyledPanel)
        
        # Determinar color según tiempo y estado
        minutos = self.orden_data['minutos_transcurridos']
        tiene_pendientes = any(i['estado_cocina'] == 'pendiente' for i in self.orden_data['items'])
        tiene_preparando = any(i['estado_cocina'] == 'preparando' for i in self.orden_data['items'])
        
        if minutos > 20:
            bg_color = "#c0392b"  # Rojo - urgente
        elif minutos > 10:
            bg_color = "#e67e22"  # Naranja - atención
        elif tiene_preparando:
            bg_color = "#2980b9"  # Azul - en preparación
        else:
            bg_color = "#27ae60"  # Verde - reciente
        
        self.setStyleSheet(f"""
            #ordenCard {{
                background-color: {bg_color};
                border-radius: 12px;
                padding: 10px;
                margin: 5px;
            }}
            QLabel {{
                color: white;
            }}
            QPushButton {{
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.5);
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.3);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header: Mesa + Tiempo
        header = QHBoxLayout()
        
        mesa_label = QLabel(self.orden_data['mesa_nombre'])
        mesa_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.addWidget(mesa_label)
        
        header.addStretch()
        
        tiempo_label = QLabel(f"⏱️ {minutos} min")
        tiempo_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.addWidget(tiempo_label)
        
        layout.addLayout(header)
        
        # Cliente
        cliente_label = QLabel(f"👤 {self.orden_data['cliente_nombre']}")
        cliente_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(cliente_label)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.3);")
        sep.setMaximumHeight(1)
        layout.addWidget(sep)
        
        # Items
        for item in self.orden_data['items']:
            item_layout = QHBoxLayout()
            
            # Estado icono
            estado = item['estado_cocina']
            if estado == 'pendiente':
                icono = "⏳"
            elif estado == 'preparando':
                icono = "🔥"
            else:
                icono = "✅"
            
            item_text = QLabel(f"{icono} {item['cantidad']}x {item['nombre']}")
            item_text.setFont(QFont("Segoe UI", 11))
            item_layout.addWidget(item_text)
            
            item_layout.addStretch()
            
            # Botón según estado
            if estado == 'pendiente':
                btn = QPushButton("Preparar")
                btn.clicked.connect(lambda checked, d=item['detalle_id']: self.marcar_preparando(d))
                item_layout.addWidget(btn)
            elif estado == 'preparando':
                btn = QPushButton("¡Listo!")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2ecc71;
                    }
                """)
                btn.clicked.connect(lambda checked, d=item['detalle_id']: self.marcar_listo(d))
                item_layout.addWidget(btn)
            
            layout.addLayout(item_layout)
        
        # Botones de acción masiva
        layout.addSpacing(10)
        btn_layout = QHBoxLayout()
        
        if tiene_pendientes:
            btn_todos_prep = QPushButton("🔥 Preparar Todos")
            btn_todos_prep.clicked.connect(self.preparar_todos)
            btn_layout.addWidget(btn_todos_prep)
        
        if tiene_preparando:
            btn_todos_listo = QPushButton("✅ Todo Listo")
            btn_todos_listo.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                }
            """)
            btn_todos_listo.clicked.connect(self.todo_listo)
            btn_layout.addWidget(btn_todos_listo)
        
        layout.addLayout(btn_layout)
    
    def marcar_preparando(self, detalle_id):
        ok, err = cocina_service.marcar_preparando(detalle_id)
        if ok:
            self.parent_view.refrescar()
        else:
            QMessageBox.warning(self, "Error", err or "No se pudo actualizar")
    
    def marcar_listo(self, detalle_id):
        ok, err = cocina_service.marcar_listo(detalle_id)
        if ok:
            self.parent_view.refrescar()
        else:
            QMessageBox.warning(self, "Error", err or "No se pudo actualizar")
    
    def preparar_todos(self):
        ok, err = cocina_service.marcar_todos_preparando(self.orden_data['orden_id'])
        if ok:
            self.parent_view.refrescar()
        else:
            QMessageBox.warning(self, "Error", err or "No se pudo actualizar")
    
    def todo_listo(self):
        ok, err = cocina_service.marcar_todos_listos(self.orden_data['orden_id'])
        if ok:
            self.parent_view.refrescar()
        else:
            QMessageBox.warning(self, "Error", err or "No se pudo actualizar")


class CocinaView(QWidget):
    """Vista principal de cocina"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refrescar()
        
        # Auto-refresh cada 10 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refrescar)
        self.timer.start(10000)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        
        titulo = QLabel("🍳 COCINA")
        titulo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50;")
        header.addWidget(titulo)
        
        header.addStretch()
        
        # Contadores de estados
        self.label_pendientes = QLabel("⏳ Pendientes: 0")
        self.label_pendientes.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.label_pendientes.setStyleSheet("""
            background-color: #e67e22;
            color: white;
            padding: 8px 15px;
            border-radius: 15px;
        """)
        header.addWidget(self.label_pendientes)
        
        self.label_preparando = QLabel("🔥 Preparando: 0")
        self.label_preparando.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.label_preparando.setStyleSheet("""
            background-color: #2980b9;
            color: white;
            padding: 8px 15px;
            border-radius: 15px;
        """)
        header.addWidget(self.label_preparando)
        
        # Botón refrescar
        btn_refresh = QPushButton("🔄 Refrescar")
        btn_refresh.setFont(QFont("Segoe UI", 11))
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4a6785;
            }
        """)
        btn_refresh.clicked.connect(self.refrescar)
        header.addWidget(btn_refresh)
        
        layout.addLayout(header)
        
        # Área de órdenes
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ecf0f1;
                border-radius: 10px;
            }
        """)
        
        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(15)
        self.grid.setContentsMargins(15, 15, 15, 15)
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        # Mensaje sin órdenes
        self.label_sin_ordenes = QLabel("✅ No hay órdenes pendientes")
        self.label_sin_ordenes.setFont(QFont("Segoe UI", 18))
        self.label_sin_ordenes.setAlignment(Qt.AlignCenter)
        self.label_sin_ordenes.setStyleSheet("color: #7f8c8d;")
        self.label_sin_ordenes.hide()
        layout.addWidget(self.label_sin_ordenes)
    
    def refrescar(self):
        """Recarga las órdenes desde la base de datos"""
        # Limpiar grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Obtener órdenes
        ordenes = cocina_service.obtener_ordenes_para_cocina()
        conteos = cocina_service.obtener_conteo_estados()
        
        # Actualizar contadores
        self.label_pendientes.setText(f"⏳ Pendientes: {conteos['pendiente']}")
        self.label_preparando.setText(f"🔥 Preparando: {conteos['preparando']}")
        
        if not ordenes:
            self.scroll.hide()
            self.label_sin_ordenes.show()
            return
        
        self.scroll.show()
        self.label_sin_ordenes.hide()
        
        # Agregar cards al grid (3 columnas)
        col = 0
        row = 0
        max_cols = 3
        
        for orden in ordenes:
            card = OrdenCard(orden, self)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Agregar espaciador al final
        self.grid.setRowStretch(row + 1, 1)
    
    def showEvent(self, event):
        """Se llama cuando la vista se muestra"""
        super().showEvent(event)
        self.refrescar()
    
    def hideEvent(self, event):
        """Se llama cuando la vista se oculta"""
        super().hideEvent(event)
