"""
ui/styles.py
Hoja de estilos Qt (QSS) con estética neobrutalista.

Paleta:
  Fondo general  #FAF3E0  (crema/hueso)
  Bordes/texto   #1A1A1A  (negro)
  Acento         #7C3AED  (morado eléctrico)
  Secundario     #2563EB  (azul)
  Muy débil      #EF4444
  Débil          #F97316
  Media          #FACC15
  Fuerte         #84CC16
  Muy fuerte     #22C55E
"""

NEOBRUTALISMO_STYLE = """
/* ================================================
   BASE
   ================================================ */
QWidget {
    background-color: #FAF3E0;
    color: #1A1A1A;
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 13px;
    selection-background-color: #7C3AED;
    selection-color: #FFFFFF;
}

QMainWindow {
    background-color: #FAF3E0;
}

/* ================================================
   HEADER DE LA APLICACIÓN
   ================================================ */
QFrame#app_header {
    background-color: #1A1A1A;
    border-bottom: 4px solid #7C3AED;
}

QLabel#titulo_app {
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
    background-color: transparent;
    letter-spacing: 1px;
}

QLabel#subtitulo_app {
    font-size: 11px;
    color: #9CA3AF;
    font-weight: normal;
    background-color: transparent;
    letter-spacing: 0.5px;
}

/* ================================================
   PESTAÑAS
   ================================================ */
QTabWidget::pane {
    border: 3px solid #1A1A1A;
    border-top: none;
    background-color: #FAF3E0;
}

QTabWidget::tab-bar {
    alignment: left;
}

QTabBar {
    background-color: #FAF3E0;
}

QTabBar::tab {
    background-color: #E5D8C0;
    color: #1A1A1A;
    border: 3px solid #1A1A1A;
    border-bottom: none;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 13px;
    margin-right: 3px;
    min-width: 110px;
}

QTabBar::tab:selected {
    background-color: #7C3AED;
    color: #FFFFFF;
    border-bottom: none;
}

QTabBar::tab:hover:!selected {
    background-color: #D4C4E8;
}

/* ================================================
   BOTONES PRIMARIOS (morado)
   ================================================ */
QPushButton {
    background-color: #7C3AED;
    color: #FFFFFF;
    border: 3px solid #1A1A1A;
    border-bottom: 5px solid #1A1A1A;
    border-right: 4px solid #1A1A1A;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
    border-radius: 0px;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #6D28D9;
}

QPushButton:pressed {
    border-bottom: 3px solid #1A1A1A;
    border-right: 3px solid #1A1A1A;
    padding-top: 10px;
    padding-left: 20px;
    padding-bottom: 6px;
    padding-right: 16px;
}

QPushButton:disabled {
    background-color: #D1D5DB;
    color: #9CA3AF;
    border: 3px solid #9CA3AF;
}

/* Botón secundario (crema con borde negro) */
QPushButton#btn_secundario {
    background-color: #FAF3E0;
    color: #1A1A1A;
    border: 3px solid #1A1A1A;
    border-bottom: 5px solid #1A1A1A;
    border-right: 4px solid #1A1A1A;
}

QPushButton#btn_secundario:hover {
    background-color: #EEE4D0;
}

QPushButton#btn_secundario:pressed {
    border-bottom: 3px solid #1A1A1A;
    border-right: 3px solid #1A1A1A;
    padding-top: 10px;
    padding-left: 20px;
    padding-bottom: 6px;
    padding-right: 16px;
}

/* Botón de exportar (azul) */
QPushButton#btn_exportar {
    background-color: #2563EB;
    color: #FFFFFF;
}

QPushButton#btn_exportar:hover {
    background-color: #1D4ED8;
}

QPushButton#btn_exportar:disabled {
    background-color: #D1D5DB;
    color: #9CA3AF;
    border: 3px solid #9CA3AF;
}

/* Botón de peligro (rojo: borrar historial, etc.) */
QPushButton#btn_peligro {
    background-color: #EF4444;
    color: #FFFFFF;
}

QPushButton#btn_peligro:hover {
    background-color: #DC2626;
}

/* Botón de idioma (en el header oscuro) */
QPushButton#btn_idioma {
    background-color: transparent;
    color: #FFFFFF;
    border: 2px solid #FFFFFF;
    border-bottom: 4px solid #FFFFFF;
    border-right: 3px solid #FFFFFF;
    padding: 5px 14px;
    font-weight: bold;
    font-size: 11px;
    min-height: 28px;
}

QPushButton#btn_idioma:hover {
    background-color: #374151;
}

QPushButton#btn_idioma:pressed {
    border-bottom: 2px solid #FFFFFF;
    border-right: 2px solid #FFFFFF;
    padding-top: 7px;
    padding-left: 16px;
}

/* ================================================
   INPUTS DE TEXTO
   ================================================ */
QLineEdit {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 3px solid #1A1A1A;
    padding: 8px 12px;
    font-size: 14px;
    border-radius: 0px;
    min-height: 32px;
}

QLineEdit:focus {
    border-color: #7C3AED;
}

QLineEdit:disabled {
    background-color: #F3F4F6;
    color: #6B7280;
    border-color: #9CA3AF;
}

QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 3px solid #1A1A1A;
    padding: 8px;
    font-size: 13px;
    border-radius: 0px;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #7C3AED;
}

/* ================================================
   GROUPBOX (tarjetas con sombra offset)
   ================================================ */
QGroupBox {
    background-color: #FFFFFF;
    border: 3px solid #1A1A1A;
    border-bottom: 6px solid #1A1A1A;
    border-right: 5px solid #1A1A1A;
    margin-top: 18px;
    padding: 12px 10px 10px 10px;
    border-radius: 0px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 4px 12px;
    background-color: #1A1A1A;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ================================================
   TABLAS
   ================================================ */
QTableWidget {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 3px solid #1A1A1A;
    gridline-color: #D1D5DB;
    font-size: 12px;
    border-radius: 0px;
    alternate-background-color: #F9FAFB;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #E5E7EB;
}

QTableWidget::item:selected {
    background-color: #EDE9FE;
    color: #1A1A1A;
}

QHeaderView::section {
    background-color: #1A1A1A;
    color: #FFFFFF;
    padding: 8px 10px;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-right: 1px solid #374151;
    border-bottom: 3px solid #7C3AED;
}

QHeaderView::section:last {
    border-right: none;
}

QTableCornerButton::section {
    background-color: #1A1A1A;
    border: none;
}

/* ================================================
   BARRA DE PROGRESO (escala de fortaleza)
   ================================================ */
QProgressBar {
    border: 3px solid #1A1A1A;
    background-color: #E5E7EB;
    height: 28px;
    text-align: center;
    font-weight: bold;
    font-size: 12px;
    border-radius: 0px;
    color: #1A1A1A;
}

QProgressBar::chunk {
    background-color: #22C55E;
    border-radius: 0px;
}

/* Clases de color para la barra de fortaleza (se asignan en Python) */
QProgressBar[nivel="0"]::chunk { background-color: #EF4444; }
QProgressBar[nivel="1"]::chunk { background-color: #F97316; }
QProgressBar[nivel="2"]::chunk { background-color: #FACC15; }
QProgressBar[nivel="3"]::chunk { background-color: #84CC16; }
QProgressBar[nivel="4"]::chunk { background-color: #22C55E; }

/* ================================================
   CHECKBOX
   ================================================ */
QCheckBox {
    spacing: 8px;
    font-size: 13px;
    background-color: transparent;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 3px solid #1A1A1A;
    background-color: #FFFFFF;
    border-radius: 0px;
}

QCheckBox::indicator:checked {
    background-color: #7C3AED;
    border: 3px solid #1A1A1A;
}

QCheckBox::indicator:hover {
    border-color: #7C3AED;
}

/* ================================================
   SPINBOX / DOUBLESPINBOX
   ================================================ */
QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 3px solid #1A1A1A;
    padding: 6px 8px;
    font-size: 13px;
    min-height: 32px;
    border-radius: 0px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #7C3AED;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #1A1A1A;
    border: none;
    width: 22px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #374151;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 7px solid #FFFFFF;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 7px solid #FFFFFF;
}

/* ================================================
   COMBOBOX
   ================================================ */
QComboBox {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 3px solid #1A1A1A;
    padding: 6px 10px;
    font-size: 13px;
    min-width: 120px;
    min-height: 32px;
    border-radius: 0px;
}

QComboBox:focus {
    border-color: #7C3AED;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 2px solid #1A1A1A;
    background-color: #1A1A1A;
}

QComboBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 8px solid #FFFFFF;
}

QComboBox QAbstractItemView {
    border: 3px solid #1A1A1A;
    background-color: #FFFFFF;
    selection-background-color: #EDE9FE;
    selection-color: #1A1A1A;
    outline: none;
}

/* ================================================
   SCROLLBAR
   ================================================ */
QScrollBar:vertical {
    background-color: #FAF3E0;
    width: 14px;
    border: 2px solid #1A1A1A;
    border-radius: 0px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #1A1A1A;
    min-height: 30px;
    border-radius: 0px;
}

QScrollBar::handle:vertical:hover {
    background-color: #374151;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}

QScrollBar:horizontal {
    background-color: #FAF3E0;
    height: 14px;
    border: 2px solid #1A1A1A;
    border-radius: 0px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #1A1A1A;
    min-width: 30px;
    border-radius: 0px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #374151;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
    background: none;
}

/* ================================================
   STATUS BAR
   ================================================ */
QStatusBar {
    background-color: #1A1A1A;
    color: #E5E7EB;
    font-weight: bold;
    font-size: 12px;
    padding: 4px 12px;
    border-top: 2px solid #7C3AED;
}

QStatusBar::item {
    border: none;
}

/* ================================================
   LABELS ESPECIALES
   ================================================ */
QLabel#placeholder_resultados {
    color: #6B7280;
    font-size: 13px;
    background-color: transparent;
    padding: 24px;
    line-height: 2.0;
}

QLabel#etiqueta_fortaleza {
    font-size: 16px;
    font-weight: bold;
}

/* ================================================
   SEPARADORES
   ================================================ */
QFrame[frameShape="4"] {
    background-color: #1A1A1A;
    max-height: 3px;
    min-height: 3px;
    border: none;
}

QFrame[frameShape="5"] {
    background-color: #1A1A1A;
    max-width: 3px;
    min-width: 3px;
    border: none;
}

/* ================================================
   DIALOG / MESSAGEBOX
   ================================================ */
QDialog {
    background-color: #FAF3E0;
    border: 3px solid #1A1A1A;
}

QMessageBox {
    background-color: #FAF3E0;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ================================================
   TOOLTIP
   ================================================ */
QToolTip {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 2px solid #7C3AED;
    padding: 4px 8px;
    font-size: 12px;
}
"""
