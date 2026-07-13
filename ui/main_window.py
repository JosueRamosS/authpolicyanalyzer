"""
ui/main_window.py
Ventana principal de AuthPolicyAnalyzer — implementación completa (Fase 4).
Contiene las 4 pestañas funcionales: Analizar, Lote CSV, Historial, Configuración.
"""
from __future__ import annotations

import os
from typing import Optional

from PyQt5.QtCore    import Qt, pyqtSlot
from PyQt5.QtGui     import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QFrame, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpinBox, QStatusBar, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget, QTabWidget,
)

from core.analyzer          import analizar, ResultadoAnalisis
from core.criteria          import Criterios
from core.dictionary_attack import simular_ataque
from core.recommendations   import generar_recomendaciones
from data.database          import DatabaseManager
from reports.json_export    import exportar_resultado, exportar_lote
from reports.pdf_report     import generar_pdf
from ui                     import i18n
from ui.widgets.strength_bar   import BarraFortaleza
from ui.widgets.thread_workers import HIBPThread, LoteThread


# ==========================================================================
# VENTANA PRINCIPAL
# ==========================================================================

class VentanaPrincipal(QMainWindow):

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self._ultimo_resultado: Optional[ResultadoAnalisis] = None
        self._lote_resultados:  list[dict] = []
        self._hibp_thread:      Optional[HIBPThread] = None
        self._lote_thread:      Optional[LoteThread] = None
        self._actualizaciones:  list        = []  # (callable) para i18n en caliente

        config = self.db.obtener_configuracion()
        i18n.cambiar_idioma(config.get("idioma", "es"))

        self._init_ui()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        self.setWindowTitle("AuthPolicyAnalyzer")
        self.setMinimumSize(1060, 780)
        self.resize(1160, 860)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._crear_header())
        root.addWidget(self._crear_cuerpo(), 1)
        self.statusBar().showMessage(i18n.t("db_ok"))

    # ==========================================================================
    # HEADER
    # ==========================================================================

    def _crear_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("app_header")
        header.setFixedHeight(82)

        lay = QHBoxLayout(header)
        lay.setContentsMargins(24, 10, 24, 10)

        branding = QVBoxLayout()
        branding.setSpacing(3)

        titulo = QLabel("AuthPolicyAnalyzer")
        titulo.setObjectName("titulo_app")

        self._lbl_subtitulo = QLabel(i18n.t("app_subtitulo"))
        self._lbl_subtitulo.setObjectName("subtitulo_app")
        self._reg(self._lbl_subtitulo, "app_subtitulo")

        branding.addWidget(titulo)
        branding.addWidget(self._lbl_subtitulo)

        lay.addLayout(branding)
        lay.addStretch()

        self.btn_idioma = QPushButton(i18n.t("idioma_actual"))
        self.btn_idioma.setObjectName("btn_idioma")
        self.btn_idioma.setFixedSize(70, 36)
        self.btn_idioma.clicked.connect(self._alternar_idioma)
        lay.addWidget(self.btn_idioma)
        return header

    # ==========================================================================
    # CUERPO CON PESTAÑAS
    # ==========================================================================

    def _crear_cuerpo(self) -> QWidget:
        contenedor = QWidget()
        lay = QVBoxLayout(contenedor)
        lay.setContentsMargins(16, 16, 16, 12)
        lay.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._crear_tab_analizar(),    i18n.t("tab_analizar"))
        self.tabs.addTab(self._crear_tab_lote(),        i18n.t("tab_lote"))
        self.tabs.addTab(self._crear_tab_historial(),   i18n.t("tab_historial"))
        self.tabs.addTab(self._crear_tab_config(),      i18n.t("tab_config"))
        self.tabs.currentChanged.connect(self._on_tab_cambio)

        lay.addWidget(self.tabs)
        return contenedor

    # ==========================================================================
    # TAB 0: ANALIZAR
    # ==========================================================================

    def _crear_tab_analizar(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(18, 18, 18, 12)
        lay.setSpacing(14)

        # --- Input ---
        self._grp_input = QGroupBox(i18n.t("contrasena_a_evaluar"))
        self._reg_grp(self._grp_input, "contrasena_a_evaluar")
        g = QHBoxLayout(self._grp_input)
        g.setContentsMargins(12, 20, 12, 12)
        g.setSpacing(10)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText(i18n.t("placeholder_input"))
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setMinimumHeight(44)
        self.input_password.returnPressed.connect(self._on_analizar)

        self.btn_toggle = QPushButton(i18n.t("btn_ver"))
        self.btn_toggle.setObjectName("btn_secundario")
        self.btn_toggle.setMinimumHeight(44)
        self.btn_toggle.setMinimumWidth(90)
        self.btn_toggle.clicked.connect(self._alternar_visibilidad)

        self.btn_analizar = QPushButton(i18n.t("btn_analizar"))
        self.btn_analizar.setMinimumHeight(44)
        self.btn_analizar.setMinimumWidth(160)
        self.btn_analizar.clicked.connect(self._on_analizar)

        g.addWidget(self.input_password)
        g.addWidget(self.btn_toggle)
        g.addWidget(self.btn_analizar)
        lay.addWidget(self._grp_input)

        # --- Scroll de resultados ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenido = QWidget()
        self._lay_resultados = QVBoxLayout(contenido)
        self._lay_resultados.setContentsMargins(0, 0, 8, 0)
        self._lay_resultados.setSpacing(12)

        # Sección fortaleza
        self._grp_fortaleza = QGroupBox(i18n.t("puntaje"))
        self._reg_grp(self._grp_fortaleza, "puntaje")
        gf = QVBoxLayout(self._grp_fortaleza)
        gf.setContentsMargins(12, 20, 12, 12)
        gf.setSpacing(10)

        self.barra_fortaleza = BarraFortaleza()
        gf.addWidget(self.barra_fortaleza)

        row_score = QHBoxLayout()
        self._lbl_entropia_val   = self._metrica_label("entropia", "—")
        self._lbl_espacio_val    = self._metrica_label("longitud", "—")
        self._lbl_score_detalle  = self._metrica_label("puntaje", "—")
        for w in (self._lbl_entropia_val, self._lbl_espacio_val, self._lbl_score_detalle):
            row_score.addWidget(w)
        gf.addLayout(row_score)
        self._lay_resultados.addWidget(self._grp_fortaleza)

        # Sección detalles
        self._grp_detalles = QGroupBox(i18n.t("detalles"))
        self._reg_grp(self._grp_detalles, "detalles")
        gd = QVBoxLayout(self._grp_detalles)
        gd.setContentsMargins(12, 20, 12, 8)

        self.tabla_detalles = QTableWidget(0, 2)
        self.tabla_detalles.horizontalHeader().hide()
        self.tabla_detalles.verticalHeader().hide()
        self.tabla_detalles.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_detalles.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_detalles.setColumnWidth(0, 200)
        self.tabla_detalles.setAlternatingRowColors(False)
        self.tabla_detalles.setShowGrid(True)
        gd.addWidget(self.tabla_detalles)
        self._lay_resultados.addWidget(self._grp_detalles)

        # Sección HIBP
        self._grp_hibp = QGroupBox(i18n.t("filtraciones"))
        self._reg_grp(self._grp_hibp, "filtraciones")
        gh = QVBoxLayout(self._grp_hibp)
        gh.setContentsMargins(12, 20, 12, 12)
        self.lbl_hibp_estado = QLabel(i18n.t("listo"))
        self.lbl_hibp_estado.setWordWrap(True)
        self.lbl_hibp_estado.setStyleSheet("font-size: 13px; background: transparent;")
        gh.addWidget(self.lbl_hibp_estado)
        self._lay_resultados.addWidget(self._grp_hibp)

        # Sección recomendaciones
        self._grp_recom = QGroupBox(i18n.t("recomendaciones"))
        self._reg_grp(self._grp_recom, "recomendaciones")
        gr = QVBoxLayout(self._grp_recom)
        gr.setContentsMargins(12, 20, 12, 12)
        self.txt_recomendaciones = QTextEdit()
        self.txt_recomendaciones.setReadOnly(True)
        self.txt_recomendaciones.setMinimumHeight(130)
        self.txt_recomendaciones.setMaximumHeight(250)
        gr.addWidget(self.txt_recomendaciones)
        self._lay_resultados.addWidget(self._grp_recom)

        self._lay_resultados.addStretch()

        # Ocultar secciones hasta el primer análisis
        for grp in (self._grp_fortaleza, self._grp_detalles,
                    self._grp_hibp, self._grp_recom):
            grp.setVisible(False)

        scroll.setWidget(contenido)
        lay.addWidget(scroll, 1)

        # Botones de exportación
        bar_exp = QHBoxLayout()
        bar_exp.setSpacing(10)
        self.btn_pdf  = QPushButton(i18n.t("btn_exportar_pdf"))
        self.btn_pdf.setObjectName("btn_exportar")
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.clicked.connect(self._exportar_pdf)
        self.btn_json = QPushButton(i18n.t("btn_exportar_json"))
        self.btn_json.setObjectName("btn_exportar")
        self.btn_json.setEnabled(False)
        self.btn_json.clicked.connect(self._exportar_json_individual)
        self._reg(self.btn_pdf,  "btn_exportar_pdf")
        self._reg(self.btn_json, "btn_exportar_json")
        bar_exp.addStretch()
        bar_exp.addWidget(self.btn_pdf)
        bar_exp.addWidget(self.btn_json)
        lay.addLayout(bar_exp)

        return widget

    # ==========================================================================
    # TAB 1: LOTE CSV
    # ==========================================================================

    def _crear_tab_lote(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(18, 18, 18, 12)
        lay.setSpacing(12)

        # Carga de archivo
        grp_carga = QGroupBox(i18n.t("lote_titulo"))
        self._reg_grp(grp_carga, "lote_titulo")
        gc = QVBoxLayout(grp_carga)
        gc.setContentsMargins(12, 20, 12, 12)
        gc.setSpacing(10)

        desc = QLabel(i18n.t("lote_descripcion"))
        desc.setObjectName("placeholder_resultados")
        self._reg(desc, "lote_descripcion")
        gc.addWidget(desc)

        fila = QHBoxLayout()
        self.btn_cargar_csv = QPushButton(i18n.t("btn_cargar_csv"))
        self.btn_cargar_csv.setMinimumHeight(40)
        self.btn_cargar_csv.setMinimumWidth(200)
        self.btn_cargar_csv.clicked.connect(self._cargar_csv)
        self._reg(self.btn_cargar_csv, "btn_cargar_csv")

        self.lbl_archivo_csv = QLabel("—")
        self.lbl_archivo_csv.setStyleSheet("font-size: 12px; color: #6B7280; background: transparent;")
        fila.addWidget(self.btn_cargar_csv)
        fila.addWidget(self.lbl_archivo_csv, 1)
        gc.addLayout(fila)

        # Barra de progreso del lote
        self.progreso_lote = QProgressBar()
        self.progreso_lote.setVisible(False)
        self.progreso_lote.setMinimumHeight(28)
        gc.addWidget(self.progreso_lote)

        self.lbl_progreso_texto = QLabel("")
        self.lbl_progreso_texto.setVisible(False)
        self.lbl_progreso_texto.setStyleSheet("font-size: 11px; color: #6B7280; background: transparent;")
        gc.addWidget(self.lbl_progreso_texto)

        lay.addWidget(grp_carga)

        # Tabla de resultados
        grp_tabla = QGroupBox(i18n.t("resultados"))
        self._reg_grp(grp_tabla, "resultados")
        gt = QVBoxLayout(grp_tabla)
        gt.setContentsMargins(12, 20, 12, 12)

        self.tabla_lote = QTableWidget(0, 7)
        self._configurar_cabecera_lote()
        self.tabla_lote.setAlternatingRowColors(True)
        self.tabla_lote.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_lote.setSelectionBehavior(QAbstractItemView.SelectRows)
        gt.addWidget(self.tabla_lote)
        lay.addWidget(grp_tabla, 1)

        # Exportar
        bar_exp = QHBoxLayout()
        self.btn_exportar_lote = QPushButton(i18n.t("btn_exportar_lote"))
        self.btn_exportar_lote.setObjectName("btn_exportar")
        self.btn_exportar_lote.setEnabled(False)
        self.btn_exportar_lote.clicked.connect(self._exportar_lote)
        self._reg(self.btn_exportar_lote, "btn_exportar_lote")
        bar_exp.addStretch()
        bar_exp.addWidget(self.btn_exportar_lote)
        lay.addLayout(bar_exp)

        return widget

    def _configurar_cabecera_lote(self) -> None:
        t = i18n.t
        cols = [
            t("csv_col_usuario"), t("csv_col_puntaje"), t("csv_col_categoria"),
            t("csv_col_entropia"), t("csv_col_contrasena"),
            t("csv_col_filtrada"), t("csv_col_politica"),
        ]
        self.tabla_lote.setHorizontalHeaderLabels(cols)
        hdr = self.tabla_lote.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeToContents)

    # ==========================================================================
    # TAB 2: HISTORIAL
    # ==========================================================================

    def _crear_tab_historial(self) -> QWidget:
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(18, 18, 18, 12)
        lay.setSpacing(12)

        # Cabecera con contador y botones
        barra = QHBoxLayout()
        self.lbl_total_hist = QLabel("")
        self.lbl_total_hist.setStyleSheet("font-weight: bold; background: transparent;")
        barra.addWidget(self.lbl_total_hist)
        barra.addStretch()

        self.btn_borrar_sel  = QPushButton(i18n.t("btn_borrar_sel"))
        self.btn_borrar_sel.setObjectName("btn_secundario")
        self.btn_borrar_sel.clicked.connect(self._borrar_evaluacion_sel)
        self._reg(self.btn_borrar_sel, "btn_borrar_sel")

        self.btn_borrar_todo = QPushButton(i18n.t("btn_borrar_todo"))
        self.btn_borrar_todo.setObjectName("btn_peligro")
        self.btn_borrar_todo.clicked.connect(self._borrar_historial)
        self._reg(self.btn_borrar_todo, "btn_borrar_todo")

        barra.addWidget(self.btn_borrar_sel)
        barra.addWidget(self.btn_borrar_todo)
        lay.addLayout(barra)

        # Tabla
        self.tabla_historial = QTableWidget(0, 8)
        self._configurar_cabecera_historial()
        self.tabla_historial.setAlternatingRowColors(True)
        self.tabla_historial.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_historial.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_historial.setSortingEnabled(True)
        lay.addWidget(self.tabla_historial, 1)

        return widget

    def _configurar_cabecera_historial(self) -> None:
        t = i18n.t
        cols = [
            t("hist_col_id"),     t("hist_col_fecha"),    t("hist_col_longitud"),
            t("hist_col_puntaje"), t("hist_col_categoria"), t("hist_col_entropia"),
            t("hist_col_filtrada"), t("hist_col_politica"),
        ]
        self.tabla_historial.setHorizontalHeaderLabels(cols)
        hdr = self.tabla_historial.horizontalHeader()
        for i in range(8):
            hdr.setSectionResizeMode(
                i, QHeaderView.Stretch if i in (1, 4) else QHeaderView.ResizeToContents
            )

    # ==========================================================================
    # TAB 3: CONFIGURACIÓN
    # ==========================================================================

    def _crear_tab_config(self) -> QWidget:
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenido = QWidget()
        lay = QVBoxLayout(contenido)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(16)

        # --- Política ---
        grp_pol = QGroupBox(i18n.t("config_titulo"))
        self._reg_grp(grp_pol, "config_titulo")
        gp = QVBoxLayout(grp_pol)
        gp.setContentsMargins(16, 22, 16, 16)
        gp.setSpacing(12)

        def fila_spin(etiqueta_key: str, min_v, max_v, step=1, sufijo=""):
            h = QHBoxLayout()
            lbl = QLabel(i18n.t(etiqueta_key))
            self._reg(lbl, etiqueta_key)
            lbl.setFixedWidth(280)
            spin = QSpinBox() if step == 1 else QDoubleSpinBox()
            spin.setRange(min_v, max_v)
            if sufijo:
                spin.setSuffix(sufijo)
            spin.setFixedWidth(120)
            h.addWidget(lbl)
            h.addWidget(spin)
            h.addStretch()
            gp.addLayout(h)
            return spin

        self.spin_longitud  = fila_spin("config_longitud", 4, 128)
        self.spin_score     = fila_spin("config_score",    0, 4)

        h_ent = QHBoxLayout()
        lbl_ent = QLabel(i18n.t("config_entropia"))
        self._reg(lbl_ent, "config_entropia")
        lbl_ent.setFixedWidth(280)
        self.spin_entropia = QDoubleSpinBox()
        self.spin_entropia.setRange(0, 300)
        self.spin_entropia.setSingleStep(5.0)
        self.spin_entropia.setSuffix(" bits")
        self.spin_entropia.setFixedWidth(120)
        h_ent.addWidget(lbl_ent)
        h_ent.addWidget(self.spin_entropia)
        h_ent.addStretch()
        gp.addLayout(h_ent)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        gp.addWidget(sep)

        def check(key: str) -> QCheckBox:
            cb = QCheckBox(i18n.t(key))
            self._reg(cb, key)
            gp.addWidget(cb)
            return cb

        self.check_may = check("config_mayusculas")
        self.check_min = check("config_minusculas")
        self.check_dig = check("config_digitos")
        self.check_sim = check("config_simbolos")

        lay.addWidget(grp_pol)

        # --- Preferencias ---
        grp_pref = QGroupBox(i18n.t("config_idioma"))
        self._reg_grp(grp_pref, "config_idioma")
        gpf = QHBoxLayout(grp_pref)
        gpf.setContentsMargins(16, 22, 16, 16)

        lbl_idioma = QLabel(i18n.t("config_idioma") + ":")
        self._reg(lbl_idioma, "config_idioma")
        self.combo_idioma = QComboBox()
        self.combo_idioma.addItems(["Español (es)", "English (en)"])
        self.combo_idioma.setFixedWidth(200)

        gpf.addWidget(lbl_idioma)
        gpf.addWidget(self.combo_idioma)
        gpf.addStretch()
        lay.addWidget(grp_pref)

        # --- Botones ---
        bar = QHBoxLayout()
        bar.setSpacing(10)
        self.btn_guardar_cfg = QPushButton(i18n.t("btn_guardar_config"))
        self.btn_guardar_cfg.setMinimumHeight(44)
        self.btn_guardar_cfg.clicked.connect(self._guardar_config)
        self._reg(self.btn_guardar_cfg, "btn_guardar_config")

        self.btn_restaurar = QPushButton(i18n.t("btn_restaurar"))
        self.btn_restaurar.setObjectName("btn_secundario")
        self.btn_restaurar.setMinimumHeight(44)
        self.btn_restaurar.clicked.connect(self._restaurar_config)
        self._reg(self.btn_restaurar, "btn_restaurar")

        bar.addStretch()
        bar.addWidget(self.btn_restaurar)
        bar.addWidget(self.btn_guardar_cfg)
        lay.addLayout(bar)
        lay.addStretch()

        scroll.setWidget(contenido)
        outer = QWidget()
        ol = QVBoxLayout(outer)
        ol.setContentsMargins(0, 0, 0, 0)
        ol.addWidget(scroll)
        self._cargar_config_en_ui()
        return outer

    # ==========================================================================
    # LÓGICA: ANÁLISIS
    # ==========================================================================

    @pyqtSlot()
    def _on_analizar(self) -> None:
        password = self.input_password.text()
        if not password:
            return

        # Cancelar HIBP anterior si sigue corriendo
        if self._hibp_thread is not None:
            try:
                if self._hibp_thread.isRunning():
                    self._hibp_thread.quit()
                    self._hibp_thread.wait(2000)
            except RuntimeError:
                pass
            self._hibp_thread = None

        config    = self.db.obtener_configuracion()
        criterios = Criterios.desde_config(config)

        dic = simular_ataque(password)
        res = analizar(password, criterios, dic)
        res.recomendaciones = generar_recomendaciones(res)

        self._ultimo_resultado = res
        self._mostrar_resultados(res)
        self._iniciar_hibp(password)

    def _mostrar_resultados(self, res: ResultadoAnalisis) -> None:
        """Rellena los widgets de resultados con los datos de un análisis."""
        t = i18n.t

        # Mostrar secciones
        for grp in (self._grp_fortaleza, self._grp_detalles,
                    self._grp_hibp, self._grp_recom):
            grp.setVisible(True)

        # Barra de fortaleza
        self.barra_fortaleza.set_puntaje(res.puntaje, t(res.clave_i18n))

        # Métricas rápidas debajo de la barra
        self._lbl_entropia_val.setText(
            f"<b>{t('entropia')}:</b> {res.entropia:.2f} {t('bits')}"
        )
        self._lbl_espacio_val.setText(
            f"<b>Espacio:</b> {res.espacio_caracteres} chars"
        )
        self._lbl_score_detalle.setText(
            f"<b>{t('puntaje')}:</b> {res.puntaje}/4"
        )

        # Tabla de detalles
        self._llenar_tabla_detalles(res)

        # HIBP — estado inicial mientras carga
        self.lbl_hibp_estado.setText(i18n.t("procesando"))
        self.lbl_hibp_estado.setStyleSheet(
            "font-size: 13px; color: #6B7280; background: transparent;"
        )

        # Recomendaciones
        self._mostrar_recomendaciones(res.recomendaciones)

    def _llenar_tabla_detalles(self, res: ResultadoAnalisis) -> None:
        t  = i18n.t
        si = lambda b: "Si" if b else "No"

        composicion = (
            f"May: {si(res.tiene_mayusculas)}  "
            f"Min: {si(res.tiene_minusculas)}  "
            f"Dig: {si(res.tiene_digitos)}  "
            f"Sim: {si(res.tiene_simbolos)}"
        )

        if res.en_diccionario:
            dic_val = (
                f"{t('encontrada_dic')} — "
                f"'{res.variante_diccionario}' ({res.esfuerzo_diccionario})"
            )
        else:
            dic_val = (
                f"{t('no_encontrada_dic')} "
                f"({res.total_variantes} variantes probadas)"
            )

        politica_val = (
            t("si_cumple") if res.cumple_politica
            else f"{t('no_cumple')}: {'; '.join(res.incumplimientos)}"
        )

        filas = [
            (t("longitud"),         f"{res.longitud} {t('caracteres')}"),
            ("Composicion",         composicion),
            (t("diccionario"),      dic_val),
            (t("cumple_politica"),  politica_val),
        ]

        # Tiempos de crackeo de zxcvbn
        if res.tiempo_crackeo:
            etiquetas = {
                "online_throttling_100_per_hour":     t("online_throttling"),
                "online_no_throttling_10_per_second": t("online_no_throttling"),
                "offline_slow_hashing_1e4_per_second": t("offline_slow_hash"),
                "offline_fast_hashing_1e10_per_second": t("offline_fast_hash"),
            }
            for k, etiq in etiquetas.items():
                val = res.tiempo_crackeo.get(k)
                if val:
                    filas.append((etiq, str(val)))

        # Colores de fila alternados pintados a mano (QSS anularía setBackground si
        # se usa setAlternatingRowColors, dejando texto blanco invisible en filas pares)
        _BG_VAL0 = QBrush(QColor("#FFFFFF"))   # valor fila par: blanco
        _BG_VAL1 = QBrush(QColor("#F3F0FF"))   # valor fila impar: lavanda suave
        _FG_VAL  = QBrush(QColor("#1A1A1A"))   # valor: negro

        self.tabla_detalles.setRowCount(len(filas))
        for i, (clave, valor) in enumerate(filas):
            bg_val = _BG_VAL1 if i % 2 else _BG_VAL0
            
            item_k = QTableWidgetItem(clave)
            item_k.setFont(QFont("", weight=QFont.Bold))
            item_k.setData(Qt.BackgroundRole, bg_val)
            item_k.setData(Qt.ForegroundRole, _FG_VAL)

            item_v = QTableWidgetItem(str(valor))
            item_v.setData(Qt.BackgroundRole, bg_val)
            item_v.setData(Qt.ForegroundRole, _FG_VAL)

            self.tabla_detalles.setItem(i, 0, item_k)
            self.tabla_detalles.setItem(i, 1, item_v)

        self.tabla_detalles.resizeRowsToContents()

    def _mostrar_recomendaciones(self, recomendaciones: list[str]) -> None:
        html_partes = []
        for idx, rec in enumerate(recomendaciones, 1):
            html_partes.append(
                f"<p style='margin:4px 0;'>"
                f"<b style='color:#7C3AED;'>{idx}.</b> {rec}"
                f"</p>"
            )
        self.txt_recomendaciones.setHtml(
            "<div style='font-family:Arial,sans-serif;font-size:12px;'>"
            + "".join(html_partes)
            + "</div>"
        )

    # ------------------------------------------------------------------
    # HIBP asíncrono
    # ------------------------------------------------------------------

    def _iniciar_hibp(self, password: str) -> None:
        self.btn_analizar.setEnabled(False)
        self.btn_analizar.setText(i18n.t("procesando"))

        self._hibp_thread = HIBPThread(password)
        self._hibp_thread.resultado.connect(self._on_hibp_resultado)
        self._hibp_thread.start()

    @pyqtSlot(dict)
    def _on_hibp_resultado(self, hibp_res: dict) -> None:
        self._hibp_thread = None   # liberar referencia; Python GC limpia el objeto
        res = self._ultimo_resultado
        if res is None:
            return

        res.en_filtraciones = hibp_res["encontrada"]
        res.veces_filtrada  = hibp_res["veces_filtrada"]
        res.hibp_disponible = hibp_res["disponible"]

        # Actualizar label HIBP
        if not hibp_res["disponible"]:
            texto = i18n.t("hibp_error")
            color = "#9CA3AF"
        elif hibp_res["encontrada"]:
            texto = f"{hibp_res['veces_filtrada']:,} {i18n.t('veces_filtrada')}"
            color = "#EF4444"
        else:
            texto = i18n.t("no_filtrada")
            color = "#22C55E"

        self.lbl_hibp_estado.setText(texto)
        self.lbl_hibp_estado.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {color}; background: transparent;"
        )

        # Recomendaciones actualizadas con info HIBP
        res.recomendaciones = generar_recomendaciones(res)
        self._mostrar_recomendaciones(res.recomendaciones)

        # Guardar en BD
        self.db.guardar_evaluacion(res.to_dict())

        # Habilitar exportaciones
        self.btn_pdf.setEnabled(True)
        self.btn_json.setEnabled(True)
        self.btn_analizar.setEnabled(True)
        self.btn_analizar.setText(i18n.t("btn_analizar"))

        n = self.db.contar_evaluaciones()
        self.statusBar().showMessage(
            i18n.t("total_registros", n=n)
        )

    # ==========================================================================
    # LÓGICA: EXPORTACIONES
    # ==========================================================================

    def _exportar_pdf(self) -> None:
        if not self._ultimo_resultado:
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "reporte_authpolicy.pdf",
            "Archivos PDF (*.pdf)"
        )
        if not ruta:
            return
        try:
            generar_pdf(self._ultimo_resultado, ruta)
            self.statusBar().showMessage(i18n.t("pdf_generado", ruta=ruta))
        except Exception as exc:
            QMessageBox.critical(self, i18n.t("error_titulo"),
                                 i18n.t("pdf_error", error=str(exc)))

    def _exportar_json_individual(self) -> None:
        if not self._ultimo_resultado:
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar JSON", "resultado_authpolicy.json",
            "Archivos JSON (*.json)"
        )
        if not ruta:
            return
        try:
            exportar_resultado(self._ultimo_resultado.to_dict(), ruta)
            self.statusBar().showMessage(f"JSON exportado: {ruta}")
        except Exception as exc:
            QMessageBox.critical(self, i18n.t("error_titulo"), str(exc))

    def _exportar_lote(self) -> None:
        if not self._lote_resultados:
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar JSON de lote", "lote_authpolicy.json",
            "Archivos JSON (*.json)"
        )
        if not ruta:
            return
        try:
            exportar_lote(self._lote_resultados, ruta)
            self.statusBar().showMessage(f"Lote exportado: {ruta}")
        except Exception as exc:
            QMessageBox.critical(self, i18n.t("error_titulo"), str(exc))

    # ==========================================================================
    # LÓGICA: LOTE CSV
    # ==========================================================================

    def _cargar_csv(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Cargar CSV", "", "CSV (*.csv);;Todos (*)"
        )
        if not ruta:
            return

        from batch.csv_processor import validar_csv
        val = validar_csv(ruta)
        if not val["valido"]:
            QMessageBox.warning(self, i18n.t("advertencia"),
                                i18n.t("csv_error_formato") + f"\n{val['error']}")
            return

        nombre = os.path.basename(ruta)
        self.lbl_archivo_csv.setText(
            f"{nombre}  —  {val['total_filas']} filas"
        )
        self._ruta_csv = ruta
        self._iniciar_lote(ruta)

    def _iniciar_lote(self, ruta: str) -> None:
        self.btn_cargar_csv.setEnabled(False)
        self.progreso_lote.setRange(0, 0)
        self.progreso_lote.setVisible(True)
        self.lbl_progreso_texto.setVisible(True)
        self.tabla_lote.setRowCount(0)
        self._lote_resultados = []
        self.btn_exportar_lote.setEnabled(False)

        config    = self.db.obtener_configuracion()
        criterios = Criterios.desde_config(config)

        self._lote_thread = LoteThread(ruta, criterios)
        self._lote_thread.progreso.connect(self._on_lote_progreso)
        self._lote_thread.completado.connect(self._on_lote_completado)
        self._lote_thread.start()

    @pyqtSlot(int, int, str)
    def _on_lote_progreso(self, actual: int, total: int, usuario: str) -> None:
        if self.progreso_lote.maximum() == 0:
            self.progreso_lote.setRange(0, total)
        self.progreso_lote.setValue(actual)
        self.lbl_progreso_texto.setText(
            f"{i18n.t('procesando')} {actual}/{total} — {usuario}"
        )

    @pyqtSlot(dict)
    def _on_lote_completado(self, resultado: dict) -> None:
        self._lote_thread = None   # liberar referencia
        self.btn_cargar_csv.setEnabled(True)
        self.progreso_lote.setVisible(False)
        self.lbl_progreso_texto.setVisible(False)

        if not resultado["exitoso"]:
            QMessageBox.critical(self, i18n.t("error_titulo"), resultado["error"])
            return

        self._lote_resultados = resultado["resultados"]
        self._llenar_tabla_lote(resultado["resultados"])

        resumen = resultado.get("resumen", {})
        self.statusBar().showMessage(
            i18n.t("lote_completo", total=resumen.get("total", 0))
        )
        self.btn_exportar_lote.setEnabled(True)

    def _llenar_tabla_lote(self, resultados: list[dict]) -> None:
        self.tabla_lote.setRowCount(len(resultados))
        colores_cat = {
            "muy_debil":  "#EF4444", "debil":     "#F97316",
            "media":      "#FACC15", "fuerte":     "#84CC16",
            "muy_fuerte": "#22C55E",
        }
        for row, r in enumerate(resultados):
            cat  = r.get("categoria", "muy_debil")
            col  = QColor(colores_cat.get(cat, "#9CA3AF"))
            vals = [
                r.get("usuario", "—"),
                str(r.get("puntaje", "—")),
                i18n.t(f"fortaleza_{cat}") if f"fortaleza_{cat}" in i18n.IDIOMAS[i18n.idioma_activo()] else cat,
                f"{r.get('entropia', 0):.1f}",
                r.get("hash_sha256", "")[:12] + "…",
                "Si" if r.get("en_filtraciones") else "No",
                "Si" if r.get("cumple_politica") else "No",
            ]
            for col_idx, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if col_idx == 2:  # categoría — coloreada
                    item.setBackground(col)
                    item.setForeground(QColor("#1A1A1A"))
                self.tabla_lote.setItem(row, col_idx, item)

        self.tabla_lote.resizeColumnsToContents()

    # ==========================================================================
    # LÓGICA: HISTORIAL
    # ==========================================================================

    def _cargar_historial(self) -> None:
        filas = self.db.obtener_historial()
        n = len(filas)
        self.lbl_total_hist.setText(i18n.t("total_registros", n=n))
        self.tabla_historial.setRowCount(n)

        colores_cat = {
            "muy_debil":  "#EF4444", "debil":     "#F97316",
            "media":      "#FACC15", "fuerte":     "#84CC16",
            "muy_fuerte": "#22C55E",
        }

        for row, r in enumerate(filas):
            cat = r.get("categoria", "")
            col = QColor(colores_cat.get(cat, "#E5E7EB"))
            datos = [
                str(r.get("id", "")),
                r.get("fecha", "")[:19].replace("T", " "),
                str(r.get("longitud", "")),
                str(r.get("puntaje", "")),
                cat,
                f"{r.get('entropia', 0):.1f}",
                "Si" if r.get("en_filtraciones") else "No",
                "Si" if r.get("cumple_politica") else "No",
            ]
            for col_idx, val in enumerate(datos):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                # Guardar id en columna 0 para borrar
                if col_idx == 0:
                    item.setData(Qt.UserRole, r.get("id"))
                if col_idx == 4:
                    item.setBackground(col)
                    item.setForeground(QColor("#1A1A1A"))
                self.tabla_historial.setItem(row, col_idx, item)

        self.tabla_historial.resizeColumnsToContents()

    def _borrar_evaluacion_sel(self) -> None:
        sel = self.tabla_historial.selectedItems()
        if not sel:
            return
        fila = self.tabla_historial.row(sel[0])
        item_id = self.tabla_historial.item(fila, 0)
        if item_id is None:
            return
        id_eval = item_id.data(Qt.UserRole)
        resp = QMessageBox.question(
            self, i18n.t("confirmar_borrar"), i18n.t("confirmar_borrar"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.db.borrar_evaluacion(id_eval)
            self._cargar_historial()

    def _borrar_historial(self) -> None:
        resp = QMessageBox.question(
            self, i18n.t("confirmar_borrar"),
            i18n.t("confirmar_borrar_todo"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.db.borrar_historial()
            self._cargar_historial()

    # ==========================================================================
    # LÓGICA: CONFIGURACIÓN
    # ==========================================================================

    def _cargar_config_en_ui(self) -> None:
        config = self.db.obtener_configuracion()
        self.spin_longitud.setValue(int(config.get("longitud_minima", 12)))
        self.spin_score.setValue(int(config.get("score_minimo", 3)))
        self.spin_entropia.setValue(float(config.get("entropia_minima", 40.0)))
        self.check_may.setChecked(config.get("requiere_mayusculas", "true") == "true")
        self.check_min.setChecked(config.get("requiere_minusculas", "true") == "true")
        self.check_dig.setChecked(config.get("requiere_digitos",    "true") == "true")
        self.check_sim.setChecked(config.get("requiere_simbolos",   "true") == "true")
        idioma = config.get("idioma", "es")
        self.combo_idioma.setCurrentIndex(0 if idioma == "es" else 1)

    def _guardar_config(self) -> None:
        idioma_idx = self.combo_idioma.currentIndex()
        idioma     = "es" if idioma_idx == 0 else "en"
        self.db.guardar_configuracion_multiple({
            "longitud_minima":    str(self.spin_longitud.value()),
            "score_minimo":       str(self.spin_score.value()),
            "entropia_minima":    str(self.spin_entropia.value()),
            "requiere_mayusculas": str(self.check_may.isChecked()).lower(),
            "requiere_minusculas": str(self.check_min.isChecked()).lower(),
            "requiere_digitos":    str(self.check_dig.isChecked()).lower(),
            "requiere_simbolos":   str(self.check_sim.isChecked()).lower(),
            "idioma":             idioma,
        })
        if idioma != i18n.idioma_activo():
            i18n.cambiar_idioma(idioma)
            self._actualizar_textos()
        self.statusBar().showMessage(i18n.t("config_guardada"))

    def _restaurar_config(self) -> None:
        resp = QMessageBox.question(
            self, i18n.t("advertencia"),
            "Restaurar todos los valores predeterminados?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            self.db.restaurar_predeterminada()
            self._cargar_config_en_ui()
            self.statusBar().showMessage(i18n.t("config_restaurada"))

    # ==========================================================================
    # INTERNACIONALIZACIÓN
    # ==========================================================================

    def _alternar_idioma(self) -> None:
        nuevo = "en" if i18n.idioma_activo() == "es" else "es"
        i18n.cambiar_idioma(nuevo)
        self.db.guardar_configuracion("idioma", nuevo)
        # Sincronizar el combo en la pestaña de configuración
        self.combo_idioma.setCurrentIndex(0 if nuevo == "es" else 1)
        self._actualizar_textos()
        self.statusBar().showMessage(i18n.t("idioma_cambiado", idioma=nuevo.upper()))

    def _actualizar_textos(self) -> None:
        """Actualiza todos los textos de la UI al idioma activo."""
        # Pestañas
        self.tabs.setTabText(0, i18n.t("tab_analizar"))
        self.tabs.setTabText(1, i18n.t("tab_lote"))
        self.tabs.setTabText(2, i18n.t("tab_historial"))
        self.tabs.setTabText(3, i18n.t("tab_config"))
        # Botón de idioma
        self.btn_idioma.setText(i18n.t("idioma_actual"))
        # Widgets registrados
        for widget, clave in self._actualizaciones:
            try:
                if isinstance(widget, QGroupBox):
                    widget.setTitle(i18n.t(clave))
                elif isinstance(widget, (QPushButton, QLabel)):
                    widget.setText(i18n.t(clave))
                elif isinstance(widget, QCheckBox):
                    widget.setText(i18n.t(clave))
            except Exception:
                pass
        # Cabeceras de tablas
        self._configurar_cabecera_lote()
        self._configurar_cabecera_historial()
        # Barra de fortaleza (si hay resultado activo)
        if self._ultimo_resultado:
            self.barra_fortaleza.set_puntaje(
                self._ultimo_resultado.puntaje,
                i18n.t(self._ultimo_resultado.clave_i18n),
            )
            self._mostrar_recomendaciones(generar_recomendaciones(self._ultimo_resultado))

    # ------------------------------------------------------------------
    # Helpers de registro para i18n
    # ------------------------------------------------------------------

    def _reg(self, widget, clave: str) -> None:
        """Registra un widget para actualización automática de idioma."""
        self._actualizaciones.append((widget, clave))

    def _reg_grp(self, grp: QGroupBox, clave: str) -> None:
        self._actualizaciones.append((grp, clave))

    # ==========================================================================
    # HELPERS VARIOS
    # ==========================================================================

    def _alternar_visibilidad(self) -> None:
        if self.input_password.echoMode() == QLineEdit.Password:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle.setText(i18n.t("btn_ocultar"))
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle.setText(i18n.t("btn_ver"))

    def _on_tab_cambio(self, index: int) -> None:
        """Carga datos perezosamente al cambiar de pestaña."""
        if index == 2:   # Historial
            self._cargar_historial()
        elif index == 3:  # Config
            self._cargar_config_en_ui()

    @staticmethod
    def _metrica_label(i18n_key: str, valor: str) -> QLabel:
        lbl = QLabel(valor)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lbl.setStyleSheet(
            "background: #FFFFFF; border: 2px solid #1A1A1A; "
            "padding: 6px 10px; font-size: 12px;"
        )
        lbl.setWordWrap(True)
        return lbl
