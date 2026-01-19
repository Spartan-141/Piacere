from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDoubleSpinBox,
    QCheckBox,
    QMessageBox,
    QComboBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...services import menu_service
from ...models import MenuSection, MenuItem


# --- Dialogs mínimos para crear/editar secciones e items ---
class SectionDialog(QDialog):
    def __init__(self, parent=None, section: Optional[MenuSection] = None):
        super().__init__(parent)
        self.setWindowTitle("Sección" if section is None else "Editar Sección")
        self.section = section
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(360)
        layout = QFormLayout(self)

        self.input_nombre = QLineEdit(self.section.nombre if self.section else "")
        self.input_descripcion = QTextEdit(
            self.section.descripcion
            if self.section and self.section.descripcion
            else ""
        )
        self.input_active = QCheckBox("Activa")
        self.input_active.setChecked(self.section.active if self.section else True)

        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Descripción:", self.input_descripcion)
        layout.addRow("", self.input_active)

        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")
        btn_guardar.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_guardar)
        layout.addRow(btn_layout)

    def values(self):
        return {
            "nombre": self.input_nombre.text().strip(),
            "descripcion": self.input_descripcion.toPlainText().strip() or None,
            "active": 1 if self.input_active.isChecked() else 0,
        }


class ItemDialog(QDialog):
    def __init__(
        self,
        parent=None,
        section_id: Optional[int] = None,
        item: Optional[MenuItem] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Item" if item is None else "Editar Item")
        self.section_id = section_id
        self.item = item
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(420)
        layout = QFormLayout(self)

        self.input_section = QComboBox()
        # cargar secciones usando objetos MenuSection
        sections = menu_service.listar_secciones(only_active=False)
        for s in sections:
            self.input_section.addItem(s.nombre, s.id)
        if self.section_id:
            idx = self.input_section.findData(self.section_id)
            if idx >= 0:
                self.input_section.setCurrentIndex(idx)

        self.input_nombre = QLineEdit(self.item.nombre if self.item else "")
        self.input_descripcion = QTextEdit(
            self.item.descripcion if self.item and self.item.descripcion else ""
        )
        self.input_descripcion.setStyleSheet("background: #1d1d1d")
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setMinimum(0.0)
        self.input_precio.setMaximum(9999.99)
        self.input_precio.setDecimals(2)
        self.input_precio.setValue(self.item.precio if self.item else 0.0)
        self.input_disponible = QCheckBox("Disponible")
        self.input_disponible.setChecked(self.item.disponible if self.item else True)

        layout.addRow("Sección:", self.input_section)
        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Descripción:", self.input_descripcion)
        layout.addRow("Precio:", self.input_precio)
        layout.addRow("", self.input_disponible)

        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")
        btn_guardar.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_guardar)
        layout.addRow(btn_layout)

    def values(self):
        return {
            "section_id": int(self.input_section.currentData()),
            "nombre": self.input_nombre.text().strip(),
            "descripcion": self.input_descripcion.toPlainText().strip() or None,
            "precio": float(self.input_precio.value()),
            "disponible": 1 if self.input_disponible.isChecked() else 0,
        }


# --- MenuView principal ---
class MenuView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh_sections()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # LEFT: Lista de secciones (compacta)
        left_panel = QVBoxLayout()
        lbl_sections = QLabel("Secciones")
        lbl_sections.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left_panel.addWidget(lbl_sections)

        self.list_sections = QListWidget()
        self.list_sections.setObjectName("list_sections")
        self.list_sections.setMaximumWidth(200)
        self.list_sections.itemSelectionChanged.connect(self.on_section_selected)
        left_panel.addWidget(self.list_sections)

        main_layout.addLayout(left_panel, 1)

        # CENTER: Tabla de items
        center_panel = QVBoxLayout()
        lbl_items = QLabel("Inventario")
        lbl_items.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_items.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(lbl_items)

        self.table_items = QTableWidget()
        self.table_items.setColumnCount(4)
        self.table_items.setHorizontalHeaderLabels(
            ["Nombre", "Descripción", "Precio", "Disponible"]
        )
        self.table_items.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_items.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_items.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self.table_items.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )
        self.table_items.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_items.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_items.setAlternatingRowColors(True)
        center_panel.addWidget(self.table_items)

        main_layout.addLayout(center_panel, 3)

        # RIGHT: Sidebar con acciones
        sidebar = QWidget()
        sidebar.setObjectName("menuSidebar")
        sidebar.setFixedWidth(240)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 8, 8, 8)
        sb_layout.setSpacing(10)

        # Búsqueda
        sb_layout.addWidget(QLabel("Buscar Items"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar items...")
        self.search_input.returnPressed.connect(self.buscar_items)
        sb_layout.addWidget(self.search_input)

        # Acciones de Sección
        sb_layout.addWidget(QLabel("Secciones"))
        self.btn_new_section = QPushButton("Nueva Sección")
        self.btn_new_section.clicked.connect(self.new_section)
        sb_layout.addWidget(self.btn_new_section)

        self.btn_edit_section = QPushButton("Editar Sección")
        self.btn_edit_section.clicked.connect(self.edit_section)
        sb_layout.addWidget(self.btn_edit_section)

        self.btn_delete_section = QPushButton("Eliminar Sección")
        self.btn_delete_section.clicked.connect(self.delete_section)
        sb_layout.addWidget(self.btn_delete_section)

        # Acciones de Items
        sb_layout.addWidget(QLabel("Items"))
        self.btn_new_item = QPushButton("Nuevo Item")
        self.btn_new_item.clicked.connect(self.new_item)
        sb_layout.addWidget(self.btn_new_item)

        self.btn_edit_item = QPushButton("Editar Item")
        self.btn_edit_item.clicked.connect(self.edit_item)
        sb_layout.addWidget(self.btn_edit_item)

        self.btn_delete_item = QPushButton("Eliminar Item")
        self.btn_delete_item.clicked.connect(self.delete_item)
        sb_layout.addWidget(self.btn_delete_item)

        # Posición de Items
        sb_layout.addWidget(QLabel("Posición"))
        self.btn_subir_item = QPushButton("↑ Subir Item")
        self.btn_subir_item.clicked.connect(self.subir_item)
        sb_layout.addWidget(self.btn_subir_item)

        self.btn_bajar_item = QPushButton("↓ Bajar Item")
        self.btn_bajar_item.clicked.connect(self.bajar_item)
        sb_layout.addWidget(self.btn_bajar_item)

        # Refrescar
        self.btn_refresh = QPushButton("Refrescar")
        self.btn_refresh.clicked.connect(self.refresh_items)
        sb_layout.addWidget(self.btn_refresh)

        sb_layout.addStretch()
        main_layout.addWidget(sidebar, 0)

    # --- Secciones ---
    def refresh_sections(self):
        self.list_sections.clear()
        sections = menu_service.listar_secciones(only_active=False)
        for sec in sections:
            item = QListWidgetItem(
                f"{sec.nombre} {'(inactiva)' if not sec.active else ''}"
            )
            font = QFont("Segoe UI", 11)
            item.setFont(font)
            item.setData(Qt.UserRole, sec)
            self.list_sections.addItem(item)
        if self.list_sections.count() > 0:
            self.list_sections.setCurrentRow(0)
        else:
            self.table_items.setRowCount(0)

    def on_section_selected(self):
        item = self.list_sections.currentItem()
        if not item:
            return
        sec = item.data(Qt.UserRole)
        self.current_section = sec
        self.refresh_items()

    def new_section(self):
        dlg = SectionDialog(self)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err, section_id = menu_service.crear_seccion(
                vals["nombre"], vals["descripcion"]
            )
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo crear la sección")
            self.refresh_sections()

    def edit_section(self):
        item = self.list_sections.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una sección")
            return
        sec = item.data(Qt.UserRole)
        dlg = SectionDialog(self, section=sec)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err = menu_service.actualizar_seccion(
                sec.id,
                vals["nombre"],
                vals["descripcion"],
                sec.position,  # Mantener position actual
                vals["active"],
            )
            if not ok:
                QMessageBox.warning(
                    self, "Error", err or "No se pudo actualizar la sección"
                )
            self.refresh_sections()

    def delete_section(self):
        item = self.list_sections.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una sección")
            return
        sec = item.data(Qt.UserRole)
        resp = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar sección '{sec.nombre}'? (se recomienda desactivarla)",
        )
        if resp == QMessageBox.Yes:
            ok, err = menu_service.eliminar_seccion(sec.id, soft=True)
            if not ok:
                QMessageBox.warning(
                    self, "Error", err or "No se pudo eliminar/desactivar la sección"
                )
            self.refresh_sections()

    # --- Items ---
    def refresh_items(self):
        sec = getattr(self, "current_section", None)
        if not sec:
            self.table_items.setRowCount(0)
            return
        section_id = sec.id
        items = menu_service.listar_items_por_seccion(section_id, only_disponible=False)
        self.table_items.setRowCount(len(items))

        for row, it in enumerate(items):
            # Columna 0: Nombre (guardar ID en UserRole)
            item_nombre = QTableWidgetItem(it.nombre or "")
            item_nombre.setData(Qt.UserRole, it.id)
            self.table_items.setItem(row, 0, item_nombre)

            # Columna 1: Descripción
            self.table_items.setItem(row, 1, QTableWidgetItem(it.descripcion or ""))

            # Columna 2: Precio
            self.table_items.setItem(
                row, 2, QTableWidgetItem(it.get_precio_formateado())
            )

            # Columna 3: Botón Toggle Disponible
            btn_toggle = QPushButton(
                "Disponible" if it.esta_disponible() else "No Disponible"
            )
            btn_toggle.setCheckable(True)
            btn_toggle.setChecked(it.esta_disponible())
            btn_toggle.setProperty("itemId", it.id)
            btn_toggle.clicked.connect(
                lambda checked, item_id=it.id: self.toggle_disponibilidad_directo(
                    item_id
                )
            )
            self.table_items.setCellWidget(row, 3, btn_toggle)

        self.table_items.resizeRowsToContents()

    def new_item(self):
        sec = getattr(self, "current_section", None)
        section_id = sec.id if sec else None
        dlg = ItemDialog(self, section_id=section_id)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err, item_id = menu_service.crear_item(
                vals["section_id"],
                vals["nombre"],
                vals["descripcion"],
                vals["precio"],
                vals["disponible"],
            )
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo crear el item")
            self.refresh_items()

    def edit_item(self):
        row = self.table_items.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un item para editar")
            return
        item_id = self.table_items.item(row, 0).data(Qt.UserRole)
        item = menu_service.obtener_item_por_id(item_id)
        if not item:
            QMessageBox.warning(self, "Error", "Item no encontrado")
            return
        dlg = ItemDialog(self, section_id=item.section_id, item=item)
        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            ok, err = menu_service.actualizar_item(
                item_id,
                vals["section_id"],
                vals["nombre"],
                vals["descripcion"],
                vals["precio"],
                vals["disponible"],
                item.position,  # Mantener position actual
            )
            if not ok:
                QMessageBox.warning(
                    self, "Error", err or "No se pudo actualizar el item"
                )
            self.refresh_items()

    def delete_item(self):
        row = self.table_items.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un item para eliminar")
            return
        item_id = self.table_items.item(row, 0).data(Qt.UserRole)
        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar item seleccionado?")
        if resp == QMessageBox.Yes:
            ok, err = menu_service.eliminar_item(item_id)
            if not ok:
                QMessageBox.warning(self, "Error", err or "No se pudo eliminar el item")
            self.refresh_items()

    def toggle_disponibilidad_directo(self, item_id: int):
        """Toggle directo desde el botón en la tabla"""
        item = menu_service.obtener_item_por_id(item_id)
        if not item:
            return

        new_disp = 0 if item.esta_disponible() else 1
        ok, err = menu_service.toggle_disponibilidad_item(item_id, new_disp)
        if not ok:
            QMessageBox.warning(
                self, "Error", err or "No se pudo cambiar disponibilidad"
            )

        self.refresh_items()

    def subir_item(self):
        """Mueve el item seleccionado una posición arriba"""
        row = self.table_items.currentRow()
        if row <= 0:
            QMessageBox.information(self, "Info", "El item ya está al inicio")
            return

        item_id = self.table_items.item(row, 0).data(Qt.UserRole)
        item_arriba_id = self.table_items.item(row - 1, 0).data(Qt.UserRole)

        ok, err = menu_service.intercambiar_positions_items(item_id, item_arriba_id)
        if not ok:
            QMessageBox.warning(self, "Error", err or "No se pudo cambiar la posición")
            return

        self.refresh_items()
        self.table_items.setCurrentCell(row - 1, 0)

    def bajar_item(self):
        """Mueve el item seleccionado una posición abajo"""
        row = self.table_items.currentRow()
        if row < 0 or row >= self.table_items.rowCount() - 1:
            QMessageBox.information(self, "Info", "El item ya está al final")
            return

        item_id = self.table_items.item(row, 0).data(Qt.UserRole)
        item_abajo_id = self.table_items.item(row + 1, 0).data(Qt.UserRole)

        ok, err = menu_service.intercambiar_positions_items(item_id, item_abajo_id)
        if not ok:
            QMessageBox.warning(self, "Error", err or "No se pudo cambiar la posición")
            return

        self.refresh_items()
        self.table_items.setCurrentCell(row + 1, 0)

    def buscar_items(self):
        term = self.search_input.text().strip()
        if not term:
            self.refresh_items()
            return

        results = menu_service.buscar_items_por_nombre(term, only_disponible=False)
        self.table_items.setRowCount(len(results))

        for row, it in enumerate(results):
            # Columna 0: Nombre
            item_nombre = QTableWidgetItem(it.nombre or "")
            item_nombre.setData(Qt.UserRole, it.id)
            self.table_items.setItem(row, 0, item_nombre)

            # Columna 1: Descripción
            self.table_items.setItem(row, 1, QTableWidgetItem(it.descripcion or ""))

            # Columna 2: Precio
            self.table_items.setItem(
                row, 2, QTableWidgetItem(it.get_precio_formateado())
            )

            # Columna 3: Botón Toggle
            btn_toggle = QPushButton(
                "✓ Disponible" if it.esta_disponible() else "✗ No Disponible"
            )
            btn_toggle.setCheckable(True)
            btn_toggle.setChecked(it.esta_disponible())
            btn_toggle.clicked.connect(
                lambda checked, item_id=it.id: self.toggle_disponibilidad_directo(
                    item_id
                )
            )
            self.table_items.setCellWidget(row, 3, btn_toggle)

        self.table_items.resizeRowsToContents()
