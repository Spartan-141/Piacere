# src/app/views/mesas/mesas_view.py
from typing import List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QScrollArea,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QGridLayout,
    QGroupBox,
    QInputDialog,
    QMenu,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ...services.mesas_service import (
    obtener_mesas,
    obtener_secciones,
    crear_mesa,
    eliminar_mesa,
    cambiar_estado_mesa,
    obtener_mesa_por_id,
    crear_seccion,
    eliminar_seccion,
)
from ...services import orden_service as orden_service_module

from .mesas_widget import MesaWidget
from ..orden.orden_view import OrdenDialog
from ..orden.orden_view_dialog import OrdenViewDialog


class MesasView(QWidget):
    mesa_seleccionada = Signal(int)
    estado_mesa_cambiado = Signal()

    def __init__(self):
        super().__init__()
        self._widgets_mesa: List[MesaWidget] = []
        self._all_mesas_cache = []
        self._all_ordenes_cache = []
        self._is_updating = False
        self._is_modal_active = False  # Nueva protección contra actualización concurrente con modales
        self.setup_ui()
        self.cargar_secciones()
        self.actualizar_mesas()

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Left: main area
        main_area = QWidget()
        main_v = QVBoxLayout(main_area)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(8)

        titulo = QLabel("CONTROL DE MESAS")
        titulo.setObjectName("mesasTitulo")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        main_v.addWidget(titulo)

        # Scroll area with grid
        self.scroll = QScrollArea()
        self.scroll.setObjectName("mesasScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("mesasScrollContent")

        self.grid = QGridLayout(self.scroll_content)
        self.grid.setContentsMargins(8, 8, 8, 8)

        self.grid.setSpacing(16)
        self.scroll.setWidget(self.scroll_content)
        main_v.addWidget(self.scroll, stretch=1)

        root.addWidget(main_area, stretch=3)

        # Right: sidebar
        sidebar = QWidget()
        sidebar.setObjectName("mesasSidebar")
        sidebar.setFixedWidth(240)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 8, 8, 8)
        sb_layout.setSpacing(10)

        # Section filter
        sb_layout.addWidget(QLabel("Sección"))
        self.combo_secciones = QComboBox()
        self.combo_secciones.setMinimumHeight(32)
        self.combo_secciones.currentIndexChanged.connect(lambda: self._on_filter_changed("combo_secciones"))
        sb_layout.addWidget(self.combo_secciones)

        # Buscador de mesas por nombre
        sb_layout.addWidget(QLabel("Buscar por nombre"))
        self.input_buscar_nombre = QLineEdit()
        self.input_buscar_nombre.setPlaceholderText("Nombre de mesa...")
        self.input_buscar_nombre.textChanged.connect(lambda: self._on_filter_changed("input_buscar_nombre"))
        sb_layout.addWidget(self.input_buscar_nombre)

        # Filtro por estado
        sb_layout.addWidget(QLabel("Filtrar por estado"))
        self.combo_estado = QComboBox()
        self.combo_estado.setMinimumHeight(32)
        self.combo_estado.addItem("Todas", None)
        self.combo_estado.addItem("Libre", "libre")
        self.combo_estado.addItem("Ocupada", "ocupado")
        self.combo_estado.addItem("Reservada", "reservada")
        self.combo_estado.currentIndexChanged.connect(lambda: self._on_filter_changed("combo_estado"))
        sb_layout.addWidget(self.combo_estado)

        # Acciones
        sb_layout.addWidget(QLabel("Mesas"))

        self.btn_agregar_mesa = QPushButton("Agregar Mesa")
        self.btn_agregar_mesa.clicked.connect(self.agregar_mesa)
        sb_layout.addWidget(self.btn_agregar_mesa)

        self.btn_editar_mesa = QPushButton("Editar Mesa")
        self.btn_editar_mesa.clicked.connect(self.editar_nombre_mesa)
        sb_layout.addWidget(self.btn_editar_mesa)

        self.btn_eliminar_mesa = QPushButton("Eliminar Mesa")
        self.btn_eliminar_mesa.clicked.connect(self.eliminar_mesa)
        sb_layout.addWidget(self.btn_eliminar_mesa)

        sb_layout.addWidget(QLabel("Secciones"))

        self.btn_agregar_seccion = QPushButton("Agregar Sección")
        self.btn_agregar_seccion.clicked.connect(self.agregar_seccion)
        sb_layout.addWidget(self.btn_agregar_seccion)

        self.btn_editar_seccion = QPushButton("Editar Sección")
        self.btn_editar_seccion.clicked.connect(self.editar_nombre_seccion)
        sb_layout.addWidget(self.btn_editar_seccion)

        self.btn_eliminar_seccion = QPushButton("Eliminar Sección")
        self.btn_eliminar_seccion.clicked.connect(self.eliminar_seccion)
        sb_layout.addWidget(self.btn_eliminar_seccion)

        # Órdenes
        sb_layout.addWidget(QLabel("Órdenes"))

        self.input_buscar_orden = QLineEdit()
        self.input_buscar_orden.setPlaceholderText("Buscar por cliente...")
        self.input_buscar_orden.returnPressed.connect(self.buscar_ordenes)
        sb_layout.addWidget(self.input_buscar_orden)

        self.btn_buscar_orden = QPushButton("Buscar Orden")
        self.btn_buscar_orden.clicked.connect(self.buscar_ordenes)
        sb_layout.addWidget(self.btn_buscar_orden)

        self.btn_ver_ordenes = QPushButton("Ver Órdenes Abiertas")
        self.btn_ver_ordenes.clicked.connect(self.mostrar_ordenes_abiertas)
        sb_layout.addWidget(self.btn_ver_ordenes)

        sb_layout.addStretch()
        root.addWidget(sidebar, stretch=0)

    def cargar_secciones(self):
        self.combo_secciones.blockSignals(True)
        try:
            self.combo_secciones.clear()
            self.combo_secciones.addItem("Todas", None)
            secciones = obtener_secciones()  # Retorna List[Seccion]
            for seccion in secciones:
                self.combo_secciones.addItem(seccion.nombre, seccion.id)
            self.combo_secciones.setCurrentIndex(0)
        finally:
            self.combo_secciones.blockSignals(False)

    def cargar_cache_mesas_y_ordenes(self):
        self._all_mesas_cache = obtener_mesas()  # Retorna List[Mesa]
        try:
            rows = orden_service_module.listar_ordenes_abiertas()
        except Exception:
            rows = []
        self._all_ordenes_cache = rows

    # Eliminado _clear_layout ya que usaremos reemplazo total de contenedor

    def _on_filter_changed(self, source):
        print(f"DEBUG: Filtro cambiado desde: {source}")
        self.actualizar_mesas()

    def actualizar_mesas(self):
        if self._is_updating:
            print("DEBUG: MesasView.actualizar_mesas() ignorado (ya en ejecución)")
            return
        
        if self._is_modal_active:
            print("DEBUG: MesasView.actualizar_mesas() BLOQUEADO (diálogo modal activo)")
            return
        
        self._is_updating = True
        print("DEBUG: MesasView.actualizar_mesas() iniciado (Estrategia: Reemplazo de Contenedor)")
        
        try:
            self.cargar_cache_mesas_y_ordenes()
            
            # DEBUG: Ver qué datos trajo el cache
            print("DEBUG: Estado de mesas en DB:")
            for m in self._all_mesas_cache:
                print(f"  - Mesa {m.numero} (ID={m.id}): {m.estado}")
            
            # 1. Crear el NUEVO contenedor y su layout
            nuevo_scroll_content = QWidget()
            nuevo_scroll_content.setObjectName("mesasScrollContent")
            nuevo_grid = QGridLayout(nuevo_scroll_content)
            nuevo_grid.setContentsMargins(8, 8, 8, 8)
            nuevo_grid.setSpacing(16)
            
            # 2. Reiniciar lista de widgets
            nuevos_widgets = []

            seccion_filtrar = self.combo_secciones.currentData()
            nombre_buscar = (self.input_buscar_nombre.text() or "").strip().lower()
            estado_filtrar = self.combo_estado.currentData()

            # Agrupar mesas por sección
            mesas_por_seccion = {}
            for mesa in self._all_mesas_cache:
                mesas_por_seccion.setdefault(mesa.seccion_id, []).append(mesa)

            if not mesas_por_seccion:
                placeholder = QLabel("No hay mesas registradas")
                placeholder.setAlignment(Qt.AlignCenter)
                nuevo_grid.addWidget(placeholder, 0, 0)
            else:
                cols = 3
                row_block = 0

                for sec_id, lista in sorted(
                    mesas_por_seccion.items(), key=lambda t: (t[0] or 0)
                ):
                    if seccion_filtrar is not None and sec_id != seccion_filtrar:
                        continue

                    # Obtener nombre de sección
                    sec_nombre = "Sin sección"
                    if sec_id:
                        secciones = obtener_secciones()
                        for s in secciones:
                            if s.id == sec_id:
                                sec_nombre = s.nombre
                                break

                    group = QGroupBox(sec_nombre)
                    inner = QGridLayout()
                    inner.setSpacing(12)
                    r = 0
                    c = 0

                    for mesa in sorted(lista, key=lambda x: x.numero):
                        if nombre_buscar and nombre_buscar not in str(mesa.numero).lower():
                            continue
                        if estado_filtrar and mesa.estado.lower() != estado_filtrar:
                            continue

                        mesa_tuple = (mesa.id, mesa.numero, mesa.estado, mesa.seccion_id, sec_nombre)
                        widget = MesaWidget(mesa_tuple, parent=nuevo_scroll_content)
                        widget.abrir_orden.connect(self._on_widget_abrir_orden)
                        widget.ver_orden.connect(self._on_widget_ver_orden_readonly)
                        widget.reservar_mesa.connect(self._on_widget_reservar_mesa)
                        widget.liberar_mesa.connect(self._on_widget_liberar_mesa)
                        widget.setContextMenuPolicy(Qt.CustomContextMenu)
                        widget.customContextMenuRequested.connect(
                            lambda pos, w=widget: self.mostrar_menu_contextual(w, pos)
                        )
                        inner.addWidget(widget, r, c)
                        nuevos_widgets.append(widget)
                        c += 1
                        if c >= cols:
                            c = 0
                            r += 1

                    group.setLayout(inner)
                    nuevo_grid.addWidget(group, row_block, 0)
                    row_block += 1
            
            # 3. CAMBIO CRÍTICO: Reemplazar el widget del scroll de una sola vez
            print("DEBUG: Aplicando nuevo contenedor al scroll area")
            old_widget = self.scroll.takeWidget()
            if old_widget:
                old_widget.deleteLater()
            
            self.scroll.setWidget(nuevo_scroll_content)
            self.scroll_content = nuevo_scroll_content
            self.grid = nuevo_grid
            self._widgets_mesa = nuevos_widgets
            
            print(f"DEBUG: MesasView.actualizar_mesas() finalizado. Widgets creados: {len(self._widgets_mesa)}")
            
        except Exception as e:
            print(f"DEBUG: Error crítico en actualizar_mesas: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._is_updating = False
            print("DEBUG: MesasView.actualizar_mesas() flag reset")

    def _on_widget_abrir_orden(self, mesa_id: int):
        self.abrir_orden(mesa_id)

    def _on_widget_ver_orden_readonly(self, mesa_id: int):
        """Abre vista de solo lectura de la orden"""
        try:
            # Obtener orden abierta de la mesa
            orden = orden_service_module.obtener_orden_abierta_por_mesa(mesa_id)
            if not orden:
                QMessageBox.information(
                    self, "Información", "No hay orden abierta para esta mesa"
                )
                return

            # Abrir diálogo de solo lectura
            dialog = OrdenViewDialog(orden.id, parent=self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo abrir la vista de orden: {e}"
            )

    def _on_widget_reservar_mesa(self, mesa_id: int):
        """Cambia el estado de la mesa a 'reservada'"""
        ok, error = cambiar_estado_mesa(mesa_id, "reservada")
        if ok:
            QMessageBox.information(self, "Éxito", "Mesa reservada exitosamente")
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", error or "No se pudo reservar la mesa")

    def _on_widget_liberar_mesa(self, mesa_id: int):
        """Libera una mesa reservada (vuelve a estado 'libre')"""
        ok, error = cambiar_estado_mesa(mesa_id, "libre")
        if ok:
            QMessageBox.information(self, "Éxito", "Mesa liberada exitosamente")
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", error or "No se pudo liberar la mesa")

    def abrir_orden(self, mesa):
        mesa_id = mesa if isinstance(mesa, int) else (mesa[0] if mesa else None)
        if mesa_id is None:
            QMessageBox.critical(self, "Error", "ID de mesa inválido")
            return

        mesa_obj = obtener_mesa_por_id(mesa_id)  # Retorna Mesa
        if not mesa_obj:
            QMessageBox.critical(self, "Error", "Mesa no encontrada")
            return

        try:
            # OrdenDialog espera tupla por compatibilidad
            mesa_tuple = (
                mesa_obj.id,
                mesa_obj.numero,
                mesa_obj.estado,
                mesa_obj.seccion_id,
                "",
            )
            # Usar el padre de más alto nivel para el diálogo (mayor estabilidad)
            dialog = OrdenDialog(mesa_tuple, parent=self.window())
            dialog.setAttribute(Qt.WA_DeleteOnClose)
            
            # Conectar señal de actualización a un timer diferido
            # from PySide6.QtCore import QTimer
            # dialog.estado_mesa_cambiado.connect(...)  <-- ELIMINADO PARA EVITAR CRASH
            
            print("DEBUG: Abriendo OrdenDialog.exec()...")
            self._is_modal_active = True
            try:
                dialog.exec()
            finally:
                self._is_modal_active = False
                
            print("DEBUG: OrdenDialog.exec() finalizado")
            
            # Forzar proceso de eventos para limpiar la UI antes de destruir nada
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            
            # Limpieza explícita del diálogo (solo variable Python, C++ ya murió por WA_DeleteOnClose)
            dialog = None
            
        except Exception as e:
            print(f"DEBUG: Error en abrir_orden: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo abrir orden: {e}")
        finally:
            # Siempre refrescar al cerrar, independientemente de errores
            print("DEBUG: Programando actualizar_mesas diferido (500ms)")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self.actualizar_mesas)

    def agregar_mesa(self):
        seccion_id = self.combo_secciones.currentData()

        # Si no hay sección seleccionada, pedir que elija una
        if seccion_id is None:
            secciones = obtener_secciones()
            if not secciones:
                QMessageBox.warning(self, "Error", "Debe crear primero una sección")
                return
            nombres = [s.nombre for s in secciones]
            nombre_sel, ok = QInputDialog.getItem(
                self,
                "Sección",
                "Seleccione sección para la nueva mesa:",
                nombres,
                0,
                False,
            )
            if not ok or not nombre_sel:
                return
            seccion_id = next((s.id for s in secciones if s.nombre == nombre_sel), None)

        if seccion_id is None:
            QMessageBox.warning(self, "Error", "Debe seleccionar una sección")
            return

        # Crear mesa con nombre auto-generado
        ok_crear, error, mesa_id = crear_mesa(seccion_id)
        if ok_crear:
            QMessageBox.information(self, "Éxito", "Mesa creada exitosamente")
            self.cargar_secciones()
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", error or "No se pudo crear la mesa")

    def eliminar_mesa(self):
        mesas = obtener_mesas()
        if not mesas:
            QMessageBox.information(self, "Información", "No hay mesas para eliminar")
            return

        numeros = [str(m.numero) for m in mesas]
        numero_seleccionado, ok = QInputDialog.getItem(
            self, "Eliminar Mesa", "Seleccione la mesa a eliminar:", numeros, 0, False
        )
        if not ok or not numero_seleccionado:
            return

        mesa_obj = next(
            (m for m in mesas if str(m.numero) == numero_seleccionado), None
        )
        if not mesa_obj:
            QMessageBox.warning(self, "Error", "Mesa no encontrada")
            return

        if mesa_obj.estado == "ocupada":
            QMessageBox.warning(self, "Error", "No se puede eliminar una mesa ocupada")
            return

        ok_del, error = eliminar_mesa(mesa_obj.id)
        if ok_del:
            QMessageBox.information(
                self, "Éxito", f"Mesa {mesa_obj.numero} eliminada correctamente"
            )
            self.cargar_secciones()
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", error or "No se pudo eliminar la mesa")

    def mostrar_menu_contextual(self, widget: MesaWidget, pos):
        m = QMenu(self)
        act_editar = m.addAction("Editar Mesa")
        act_toggle = m.addAction("Alternar Estado")
        act_abrir = m.addAction("Abrir Orden")
        accion = m.exec_(widget.mapToGlobal(pos))

        if accion == act_editar:
            self.editar_mesa(widget.mesa_id)
        elif accion == act_toggle:
            nuevo = "libre" if widget.estado != "libre" else "ocupada"
            ok, error = cambiar_estado_mesa(widget.mesa_id, nuevo)
            if ok:
                widget.actualizar_estado(nuevo)
                self.estado_mesa_cambiado.emit()
            else:
                QMessageBox.critical(
                    self, "Error", error or "No se pudo cambiar el estado"
                )
        elif accion == act_abrir:
            self.abrir_orden(widget.mesa_id)

    def agregar_seccion(self):
        nombre, ok = QInputDialog.getText(
            self, "Nueva Sección", "Nombre de la sección:"
        )
        if not ok or not nombre.strip():
            return

        ok_crear, error, seccion_id = crear_seccion(nombre.strip())
        if ok_crear:
            QMessageBox.information(self, "Éxito", f"Sección '{nombre}' creada")
            self.cargar_secciones()
            self.actualizar_mesas()
        else:
            QMessageBox.critical(self, "Error", error or "No se pudo crear la sección")

    def eliminar_seccion(self):
        """Elimina una sección con lógica inteligente según estado de mesas"""
        secciones = obtener_secciones()
        if not secciones:
            QMessageBox.information(self, "Información", "No hay secciones registradas")
            return

        # Seleccionar sección
        nombres = [s.nombre for s in secciones]
        nombre_sel, ok = QInputDialog.getItem(
            self,
            "Eliminar Sección",
            "Seleccione la sección a eliminar:",
            nombres,
            0,
            False,
        )
        if not ok or not nombre_sel:
            return

        sec_id = next((s.id for s in secciones if s.nombre == nombre_sel), None)
        if sec_id is None:
            QMessageBox.warning(self, "Error", "Sección no encontrada")
            return

        # Obtener todas las mesas de esta sección
        todas_mesas = obtener_mesas()
        mesas_seccion = [m for m in todas_mesas if m.seccion_id == sec_id]

        if not mesas_seccion:
            # Sin mesas, eliminar sección directamente
            ok_del, error = eliminar_seccion(sec_id)
            if ok_del:
                QMessageBox.information(
                    self, "Éxito", f"Sección '{nombre_sel}' eliminada"
                )
                self.cargar_secciones()
                self.actualizar_mesas()
            else:
                QMessageBox.critical(
                    self, "Error", error or "No se pudo eliminar la sección"
                )
            return

        # Clasificar mesas por estado
        mesas_ocupadas = [
            m for m in mesas_seccion if m.estado in ["ocupado", "reservada"]
        ]
        mesas_libres = [m for m in mesas_seccion if m.estado == "libre"]

        if mesas_ocupadas:
            # Hay mesas ocupadas/reservadas
            msg = f"La sección '{nombre_sel}' tiene {len(mesas_ocupadas)} mesa(s) ocupada(s) o reservada(s):\n\n"
            for m in mesas_ocupadas:
                msg += f"  • {m.numero} ({m.estado})\n"

            if mesas_libres:
                msg += f"\nHay {len(mesas_libres)} mesa(s) libre(s).\n"
                msg += "\n¿Desea eliminar solo las mesas libres?"

                reply = QMessageBox.question(
                    self,
                    "Advertencia",
                    msg,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    # Eliminar solo mesas libres
                    eliminadas = 0
                    for m in mesas_libres:
                        ok_del, _ = eliminar_mesa(m.id)
                        if ok_del:
                            eliminadas += 1

                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"{eliminadas} mesa(s) libre(s) eliminada(s).\n"
                        f"La sección se mantendrá con {len(mesas_ocupadas)} mesa(s).",
                    )
                    self.cargar_secciones()
                    self.actualizar_mesas()
            else:
                # Solo mesas ocupadas, no se puede eliminar
                msg += "\nNo se puede eliminar la sección."
                QMessageBox.warning(self, "Advertencia", msg)

        else:
            # Todas las mesas están libres
            msg = f"¿Eliminar sección '{nombre_sel}' y sus {len(mesas_libres)} mesa(s)?"
            reply = QMessageBox.question(
                self,
                "Confirmar",
                msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                # Eliminar todas las mesas y la sección
                eliminadas = 0
                for m in mesas_libres:
                    ok_del, _ = eliminar_mesa(m.id)
                    if ok_del:
                        eliminadas += 1

                # Eliminar sección
                ok_del, error = eliminar_seccion(sec_id)
                if ok_del:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"Sección '{nombre_sel}' y {eliminadas} mesa(s) eliminadas",
                    )
                    self.cargar_secciones()
                    self.actualizar_mesas()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        error or "No se pudo eliminar la sección",
                    )

    def editar_nombre_mesa(self):
        """Permite editar el número de una mesa"""
        mesas = obtener_mesas()
        if not mesas:
            QMessageBox.information(self, "Información", "No hay mesas para editar")
            return

        # Seleccionar mesa
        nombres = [str(m.numero) for m in mesas]
        nombre_sel, ok = QInputDialog.getItem(
            self, "Editar Mesa", "Seleccione la mesa a editar:", nombres, 0, False
        )
        if not ok or not nombre_sel:
            return

        mesa_obj = next((m for m in mesas if str(m.numero) == nombre_sel), None)
        if not mesa_obj:
            QMessageBox.warning(self, "Error", "Mesa no encontrada")
            return

        # Pedir nuevo número
        nuevo_numero, ok = QInputDialog.getInt(
            self,
            "Nuevo Número",
            f"Ingrese el nuevo número para {mesa_obj.numero}:",
            1,
            1,
            999,
        )
        if not ok:
            return

        # Obtener inicial de la sección
        from ...services.mesas_service import obtener_inicial_seccion

        inicial = obtener_inicial_seccion(mesa_obj.seccion_id)
        nuevo_nombre = f"Mesa {inicial}{nuevo_numero}"

        # Verificar disponibilidad
        if any(m.numero == nuevo_nombre for m in mesas if m.id != mesa_obj.id):
            QMessageBox.warning(
                self, "Error", f"El nombre '{nuevo_nombre}' ya está en uso"
            )
            return

        # Actualizar
        from ...services.mesas_service import actualizar_mesa

        ok_upd, error = actualizar_mesa(
            mesa_obj.id, nuevo_nombre, mesa_obj.estado, mesa_obj.seccion_id
        )
        if ok_upd:
            QMessageBox.information(
                self, "Éxito", f"Mesa renombrada a '{nuevo_nombre}'"
            )
            self.actualizar_mesas()
        else:
            QMessageBox.critical(
                self, "Error", error or "No se pudo actualizar la mesa"
            )

    def editar_nombre_seccion(self):
        """Permite editar el nombre de una sección y regenera nombres de mesas"""
        secciones = obtener_secciones()
        if not secciones:
            QMessageBox.information(self, "Información", "No hay secciones para editar")
            return

        # Seleccionar sección
        nombres = [s.nombre for s in secciones]
        nombre_sel, ok = QInputDialog.getItem(
            self,
            "Editar Sección",
            "Seleccione la sección a editar:",
            nombres,
            0,
            False,
        )
        if not ok or not nombre_sel:
            return

        sec_obj = next((s for s in secciones if s.nombre == nombre_sel), None)
        if not sec_obj:
            QMessageBox.warning(self, "Error", "Sección no encontrada")
            return

        # Pedir nuevo nombre
        nuevo_nombre, ok = QInputDialog.getText(
            self,
            "Nuevo Nombre",
            f"Ingrese el nuevo nombre para '{sec_obj.nombre}':",
            text=sec_obj.nombre,
        )
        if not ok or not nuevo_nombre.strip():
            return

        nuevo_nombre = nuevo_nombre.strip()

        # Verificar disponibilidad
        if any(s.nombre == nuevo_nombre for s in secciones if s.id != sec_obj.id):
            QMessageBox.warning(
                self, "Error", f"El nombre '{nuevo_nombre}' ya está en uso"
            )
            return

        # Actualizar sección y regenerar nombres de mesas
        from ...services.mesas_service import (
            actualizar_mesa,
            obtener_siguiente_numero_mesa,
        )
        from ...db.connection import crear_conexion

        try:
            conn = crear_conexion()
            cur = conn.cursor()

            # Actualizar nombre de sección
            cur.execute(
                "UPDATE secciones SET nombre = ? WHERE id = ?",
                (nuevo_nombre, sec_obj.id),
            )

            # Obtener mesas de esta sección
            mesas_seccion = [m for m in obtener_mesas() if m.seccion_id == sec_obj.id]

            # Regenerar nombres con nueva inicial
            nueva_inicial = nuevo_nombre[0].upper()
            for i, mesa in enumerate(sorted(mesas_seccion, key=lambda x: x.numero), 1):
                nuevo_nombre_mesa = f"Mesa {nueva_inicial}{i}"
                cur.execute(
                    "UPDATE mesas SET numero = ? WHERE id = ?",
                    (nuevo_nombre_mesa, mesa.id),
                )

            conn.commit()
            conn.close()

            QMessageBox.information(
                self,
                "Éxito",
                f"Sección renombrada y {len(mesas_seccion)} mesa(s) actualizadas",
            )
            self.cargar_secciones()
            self.actualizar_mesas()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo actualizar la sección: {e}"
            )

    def buscar_ordenes(self):
        """Busca órdenes por nombre de cliente"""
        nombre_cliente = self.input_buscar_orden.text().strip()
        if not nombre_cliente:
            QMessageBox.information(
                self, "Información", "Ingrese un nombre de cliente para buscar"
            )
            return

        # Buscar órdenes
        try:
            from ...db.connection import crear_conexion

            conn = crear_conexion()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT o.id, o.cliente_nombre, o.total, o.estado, m.numero
                FROM ordenes o
                JOIN mesas m ON o.mesa_id = m.id
                WHERE o.cliente_nombre LIKE ? AND o.estado = 'abierta'
            """,
                (f"%{nombre_cliente}%",),
            )
            resultados = cur.fetchall()
            conn.close()

            if not resultados:
                QMessageBox.information(
                    self,
                    "Sin resultados",
                    f"No se encontraron órdenes para '{nombre_cliente}'",
                )
                return

            # Mostrar resultados en diálogo
            from .ordenes_dialog import OrdenesDialog

            dialog = OrdenesDialog(resultados, parent=self)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar órdenes: {e}")

    def mostrar_ordenes_abiertas(self):
        """Muestra todas las órdenes abiertas"""
        try:
            from ...db.connection import crear_conexion

            conn = crear_conexion()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT o.id, o.cliente_nombre, o.total, o.estado, m.numero
                FROM ordenes o
                JOIN mesas m ON o.mesa_id = m.id
                WHERE o.estado = 'abierta'
                ORDER BY m.numero
            """
            )
            resultados = cur.fetchall()
            conn.close()

            if not resultados:
                QMessageBox.information(self, "Información", "No hay órdenes abiertas")
                return

            # Mostrar resultados en diálogo
            from .ordenes_dialog import OrdenesDialog

            dialog = OrdenesDialog(resultados, parent=self)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al obtener órdenes: {e}")
