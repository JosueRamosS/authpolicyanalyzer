"""
main.py
Punto de entrada de AuthPolicyAnalyzer.
Ejecutar con:  python main.py
"""
import sys
import os

# Garantiza que el paquete se resuelva desde el directorio del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt

from data.database import DatabaseManager
from ui.main_window import VentanaPrincipal
from ui.styles import NEOBRUTALISMO_STYLE


def main() -> None:
    # Habilitar escalado para pantallas HiDPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("AuthPolicyAnalyzer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AuthPolicyAnalyzer – Proyecto Académico")

    fuente = QFont("Arial", 13)
    fuente.setStyleHint(QFont.SansSerif)
    app.setFont(fuente)

    # Aplicar hoja de estilos neobrutalista
    app.setStyleSheet(NEOBRUTALISMO_STYLE)

    # Inicializar base de datos
    try:
        db = DatabaseManager()
        db.inicializar()
    except Exception as exc:
        QMessageBox.critical(
            None,
            "Error de base de datos",
            f"No se pudo inicializar la base de datos:\n\n{exc}",
        )
        sys.exit(1)

    # Crear y mostrar la ventana principal
    ventana = VentanaPrincipal(db)
    ventana.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
