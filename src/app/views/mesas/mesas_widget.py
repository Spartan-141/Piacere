from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class MesaWidget(QWidget):
    """
    Widget visual para representar una mesa:
      - muestra número (o nombre)
      - etiqueta de estado (libre / ocupado / reservada)
      - botones: Abrir/Continuar Orden, Ver Orden (modal)
    Señales:
      - abrir_orden(mesa_id)
      - ver_orden(mesa_id)
      - cancelar_accion(mesa_id)  <-- opcional para extensiones
    """

    abrir_orden = Signal(int)
    ver_orden = Signal(int)
    reservar_mesa = Signal(int)
    liberar_mesa = Signal(int)
    cancelar_accion = Signal(int)

    def __init__(
        self,
        mesa_tuple: Tuple[int, int, str, Optional[int], Optional[str]],
        parent=None,
    ):
        """
        mesa_tuple puede ser:
          (id, numero, estado)  o  (id, numero, estado, seccion_id, seccion_nombre)
        """
        super().__init__(parent)
        # propiedades
        self.mesa_id = int(mesa_tuple[0])
        self.numero = mesa_tuple[1]
        self.estado = mesa_tuple[2]
        self.seccion_id = mesa_tuple[3] if len(mesa_tuple) > 3 else None
        self.seccion_nombre = mesa_tuple[4] if len(mesa_tuple) > 4 else None

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(220, 120)

        self._build_ui()
        self.actualizar_estado(self.estado)

    # UI
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(6)

        # Card frame (bordes y sombra mínima)
        self.card = QFrame()
        self.card.setObjectName("mesaCard")
        self.card.setFrameShape(QFrame.StyledPanel)
        self.card.setLineWidth(1)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(6)

        # Top: nombre de la mesa
        self.label_nombre = QLabel(self.numero)
        self.label_nombre.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.label_nombre.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        card_layout.addWidget(self.label_nombre)

        # Estado (badge)
        self.label_estado = QLabel("")
        self.label_estado.setFont(QFont("Segoe UI", 9))
        self.label_estado.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label_estado.setFixedHeight(22)
        self.label_estado.setContentsMargins(6, 2, 6, 2)
        self.label_estado.setObjectName("mesaBadge")
        card_layout.addWidget(self.label_estado)

        # Spacer
        card_layout.addStretch()

        # Botones en fila inferior
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        # Botón Abrir/Continuar
        self.btn_abrir = QPushButton("Abrir")
        self.btn_abrir.setCursor(Qt.PointingHandCursor)
        self.btn_abrir.setMinimumHeight(28)
        self.btn_abrir.setObjectName("mesaOpenBtn")
        self.btn_abrir.clicked.connect(self._on_abrir_clicked)

        # Botón Ver Orden
        self.btn_ver = QPushButton("Ver Orden")
        self.btn_ver.setCursor(Qt.PointingHandCursor)
        self.btn_ver.setMinimumHeight(28)
        self.btn_ver.setObjectName("mesaViewBtn")
        self.btn_ver.clicked.connect(self._on_ver_clicked)

        # Botón Reservar
        self.btn_reservar = QPushButton("Reservar")
        self.btn_reservar.setCursor(Qt.PointingHandCursor)
        self.btn_reservar.setMinimumHeight(28)
        self.btn_reservar.setObjectName("mesaReserveBtn")
        self.btn_reservar.clicked.connect(self._on_reservar_clicked)

        # Botón Liberar
        self.btn_liberar = QPushButton("Liberar")
        self.btn_liberar.setCursor(Qt.PointingHandCursor)
        self.btn_liberar.setMinimumHeight(28)
        self.btn_liberar.setObjectName("mesaReleaseBtn")
        self.btn_liberar.clicked.connect(self._on_liberar_clicked)

        btn_row.addWidget(self.btn_abrir)
        btn_row.addWidget(self.btn_ver)
        btn_row.addWidget(self.btn_reservar)
        btn_row.addWidget(self.btn_liberar)

        card_layout.addLayout(btn_row)

        outer.addWidget(self.card)

        # Estilos inline mínimos (puedes moverlos a .qss)

    # Actualización visual según estado
    def actualizar_estado(self, nuevo_estado: str):
        self.estado = nuevo_estado or "libre"
        estado = self.estado.lower()

        # Badge text y color
        if estado == "ocupado":
            text = "Ocupada"
        elif estado == "reservada":
            text = "Reservada"
        else:
            text = "Libre"

        self.label_estado.setText(f"Estado: {text}")

        # Asignar propiedad dinámica para estilizar en styles.py
        self.label_estado.setProperty("estado", estado)
        self.label_estado.style().unpolish(self.label_estado)
        self.label_estado.style().polish(self.label_estado)

        # Lógica condicional de botones según estado
        if estado == "libre":
            # Libre: Mostrar "Abrir" + "Reservar"
            self.btn_abrir.setText("Abrir")
            self.btn_abrir.setVisible(True)
            self.btn_ver.setVisible(False)
            self.btn_reservar.setVisible(True)
            self.btn_liberar.setVisible(False)

        elif estado == "reservada":
            # Reservada: Mostrar "Abrir" + "Liberar"
            self.btn_abrir.setText("Abrir")
            self.btn_abrir.setVisible(True)
            self.btn_ver.setVisible(False)
            self.btn_reservar.setVisible(False)
            self.btn_liberar.setVisible(True)

        else:  # ocupado
            # Ocupada: Mostrar "Continuar" + "Ver Orden"
            self.btn_abrir.setText("Continuar")
            self.btn_abrir.setVisible(True)
            self.btn_ver.setVisible(True)
            self.btn_reservar.setVisible(False)
            self.btn_liberar.setVisible(False)

    # Eventos
    def _on_abrir_clicked(self):
        # Emitir señal para que el controlador abra o cree orden
        self.abrir_orden.emit(self.mesa_id)

    def _on_ver_clicked(self):
        self.ver_orden.emit(self.mesa_id)

    def _on_reservar_clicked(self):
        self.reservar_mesa.emit(self.mesa_id)

    def _on_liberar_clicked(self):
        self.liberar_mesa.emit(self.mesa_id)

    # API auxiliar
    def set_seccion(self, nombre: str):
        self.seccion_nombre = nombre
        self.setToolTip(f"Mesa {self.numero} — Sección: {nombre}")

    def set_numero(self, numero):
        self.numero = numero
        self.label_nombre.setText(f"Mesa {self.numero}")

    def set_disabled(self, disabled: bool):
        self.setEnabled(not disabled)
