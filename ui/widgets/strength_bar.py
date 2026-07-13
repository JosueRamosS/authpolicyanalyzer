"""
ui/widgets/strength_bar.py
Barra de progreso personalizada para visualizar la fortaleza de la contraseña.
Cambia de color según el nivel (0-4) y muestra la etiqueta de categoría.
"""
from __future__ import annotations

from PyQt5.QtWidgets import QProgressBar


class BarraFortaleza(QProgressBar):
    """Barra de progreso con color dinámico según el score de fortaleza."""

    _COLORES = [
        "#EF4444",  # 0 — muy débil
        "#F97316",  # 1 — débil
        "#FACC15",  # 2 — media
        "#84CC16",  # 3 — fuerte
        "#22C55E",  # 4 — muy fuerte
    ]
    # Porcentajes visuales por nivel (no lineales para mejor percepción)
    _VALORES = [10, 28, 50, 72, 96]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setMinimumHeight(36)
        self.setFormat("")
        self.setTextVisible(True)

    def set_puntaje(self, puntaje: int, etiqueta: str) -> None:
        """Actualiza la barra con el puntaje (0-4) y la etiqueta traducida."""
        n = max(0, min(puntaje, 4))
        self.setValue(self._VALORES[n])
        self.setFormat(f"  {etiqueta.upper()}  ({n} / 4)")
        self._aplicar_color(n)

    def limpiar(self) -> None:
        self.setValue(0)
        self.setFormat("")
        self.setStyleSheet("")

    def _aplicar_color(self, n: int) -> None:
        color = self._COLORES[n]
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 3px solid #1A1A1A;
                border-bottom: 5px solid #1A1A1A;
                border-right:  4px solid #1A1A1A;
                background-color: #E5E7EB;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
                color: #1A1A1A;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
