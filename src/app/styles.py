# src/app/styles.py

DARK_STYLES = """
/* ========================================================================
   1. ESTILOS GLOBALES Y RESET
   ======================================================================== */
* {
    color: #ffffff;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

QFrame {
    border: none;
}

QLabel {
    color: #ffffff;
}

/* ========================================================================
   2. COMPONENTES ESTÁNDAR (Inputs, Botones, Tablas)
   ======================================================================== */

/* --- Campos de Entrada (General) --- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    border-radius: 6px;
    padding: 6px 10px;
    border: 1px solid #555555;
    background-color: #2b2b2b;
    min-height: 25px;
    color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 2px solid #888888;
}

QTextEdit {
    background-color: #1d1d1d; /* Un poco más oscuro para áreas de texto */
}

/* --- Botones Generales --- */
QPushButton {
    color: #ffffff;
    border: none;
    padding: 5px;
}

QPushButton:hover {
    background-color: #3c3c3c;
}

QPushButton:pressed {
    background-color: #555555;
}

/* --- Tablas (QTableWidget) --- */
QTableWidget {
    background-color: #2b2b2b;
    gridline-color: #b4b4b4;
    selection-background-color: #5b5b5b;
    selection-color: #ffffff;
    alternate-background-color: #3b3b3b;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #2b2b2b;
    color: #ffffff;
    padding: 6px;
    border: none;
    font-weight: bold;
}

/* --- Calendario (QCalendarWidget) --- */
QCalendarWidget {
    background-color: #f0f0f0;
    border: 1px solid #888;
}

QCalendarWidget QToolButton {
    background-color: #3498db;
    color: white;
    font-weight: bold;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QToolButton:hover {
    background-color: #2980b9;
}

QCalendarWidget QAbstractItemView {
    background-color: white;
    selection-background-color: #3498db;
    selection-color: white;
}

QCalendarWidget QAbstractItemView:enabled {
    color: black;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #aaa;
}

/* ========================================================================
   3. LAYOUT PRINCIPAL (Sidebar y Main)
   ======================================================================== */
QFrame#main {
    background-color: #0a0a0a;
}

QFrame#sidebar {
    background-color: #1d1d1d;
}

QLabel#label_2 {
    font: 700 15pt "Segoe UI";
}

/* Botones del Sidebar Principal */
QFrame#sidebar QPushButton {
    background-color: transparent;
    color: white;
    border: none;
    border-radius: 8px;
    text-align: left;
    margin-left: 10px;
    padding: 10px 10px;
    font-size: 16px;
}

QFrame#sidebar QPushButton:hover {
    background-color: #2d2d2d;
}

QFrame#sidebar QPushButton:pressed {
    background-color: #555555;
}

/* ========================================================================
   4. MÓDULO: MESAS
   ======================================================================== */

/* Sidebar del Módulo Mesas */
QWidget#mesasSidebar {
    background-color: #2b2b2b;
    border-radius: 8px;
    border: 1px solid #444444;
}

QWidget#mesasSidebar QPushButton {
    background-color: #3a3a3a;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px;
    margin: 2px 0;
    text-align: left;
}

QWidget#mesasSidebar QPushButton:hover {
    background-color: #4a4a4a;
}

QWidget#mesasSidebar QPushButton:pressed {
    background-color: #2a2a2a;
}

/* Tarjeta de Mesa (MesaWidget) */
QFrame#mesaCard {
    border-radius: 8px;
    border: 1px solid #f5f5f5;
    background-color: #333333;
}

QFrame#mesaCard:hover {
    border: 2px solid #ffffff;
    background-color: #808080;
}

QFrame#mesaCard QLabel {
    color: #ffffff;
    background-color: transparent;
}

/* Badge de Estado (Libre, Ocupada, Reservada) */
QLabel#mesaBadge {
    border-radius: 6px;
    padding: 2px 6px;
    font-weight: 600;
    color: white;
}

QLabel#mesaBadge[estado="libre"] {
    background-color: #16a085;
}

QLabel#mesaBadge[estado="ocupado"] {
    background-color: #c0392b;
}

QLabel#mesaBadge[estado="reservada"] {
    background-color: #f39c12;
    color: black;
}

/* Botones de Acción en la Tarjeta de Mesa */
QPushButton#mesaOpenBtn {
    background-color: #2d86c9;
    color: white;
    border-radius: 6px;
    padding: 4px 8px;
}
QPushButton#mesaOpenBtn:hover { background-color: #256fa8; }

QPushButton#mesaViewBtn {
    background-color: #7d8b95;
    color: white;
    border-radius: 6px;
    padding: 4px 8px;
}
QPushButton#mesaViewBtn:hover { background-color: #6b7780; }

QPushButton#mesaReserveBtn {
    background-color: #f39c12;
    color: white;
    border-radius: 6px;
    padding: 4px 8px;
}
QPushButton#mesaReserveBtn:hover { background-color: #e67e22; }

QPushButton#mesaReleaseBtn {
    background-color: #95a5a6;
    color: white;
    border-radius: 6px;
    padding: 4px 8px;
}
QPushButton#mesaReleaseBtn:hover { background-color: #7f8c8d; }


/* ========================================================================
   5. MÓDULO: MENÚ
   ======================================================================== */
QListWidget#list_sections {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 6px;
}

/* Sidebar del Menú */
QWidget#menuSidebar {
    background-color: #2b2b2b;
    border-radius: 8px;
    border: 1px solid #444444;
}

QWidget#menuSidebar QLabel {
    color: #ffffff;
    font-weight: bold;
    margin-top: 10px;
    font-size: 11px;
}

QWidget#menuSidebar QPushButton {
    background-color: #3a3a3a;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px;
    margin: 2px 0;
    text-align: left;
}

QWidget#menuSidebar QPushButton:hover {
    background-color: #4a4a4a;
}

QWidget#menuSidebar QPushButton:pressed {
    background-color: #2a2a2a;
}

/* Botones de disponibilidad (Checkable) */
QPushButton[checkable="true"] {
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: bold;
    margin: 5px;
}

QPushButton[checkable="true"]:checked {
    background-color: #27ae60;
    color: white;
}

QPushButton[checkable="true"]:!checked {
    background-color: #e74c3c;
    color: white;
}

QPushButton[checkable="true"]:hover {
    opacity: 0.8;
}

/* ========================================================================
   6. MÓDULO: TASA CAMBIO
   ======================================================================== */
QFrame#tasaActualFrame {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #2c3e50, stop:1 #34495e
    );
    border-radius: 12px;
    padding: 20px;
    border: 2px solid #3498db;
}

QFrame#tasaActualFrame QLabel {
    color: #ecf0f1;
}

QGroupBox {
    font-weight: bold;
    font-size: 12px;
    color: #ffffff;
    border: 2px solid #444444;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    background-color: #1a1a1a;
}

/* Estilos Específicos para SpinBox con flechas personalizadas */
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #3a3a3a;
    border: none;
    width: 20px;
    border-radius: 2px;
}

QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #4a4a4a;
}

QDoubleSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 6px solid #ffffff;
    width: 0;
    height: 0;
}

QDoubleSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #ffffff;
    width: 0;
    height: 0;
}

/* ========================================================================
   7. MÓDULO: REPORTES
   ======================================================================== */
QFrame#ventasMetricasFrame {
    background-color: #2c3e50;
    border-radius: 8px;
    padding: 15px;
    border: 1px solid #3498db;
}

QFrame#ventasMetricasFrame QLabel {
    color: #ecf0f1;
}
"""