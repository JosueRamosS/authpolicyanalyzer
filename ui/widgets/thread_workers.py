"""
ui/widgets/thread_workers.py
Workers QThread para operaciones de red y lote que no deben
bloquear el hilo principal de la interfaz gráfica.
"""
from __future__ import annotations

from PyQt5.QtCore import QThread, pyqtSignal


class HIBPThread(QThread):
    """
    Verifica una contraseña contra la API Pwned Passwords de HIBP
    en un hilo separado para no bloquear la UI.
    """
    resultado = pyqtSignal(dict)

    def __init__(self, password: str, parent=None):
        super().__init__(parent)
        self._password = password

    def run(self) -> None:
        from services.hibp import verificar
        try:
            res = verificar(self._password)
        except Exception:
            res = {"encontrada": False, "veces_filtrada": 0, "disponible": False}
        self.resultado.emit(res)


class LoteThread(QThread):
    """
    Procesa un archivo CSV en lote en un hilo separado.
    Emite señales de progreso durante el procesamiento.
    """
    progreso   = pyqtSignal(int, int, str)   # (actual, total, usuario)
    completado = pyqtSignal(dict)

    def __init__(self, ruta: str, criterios, incluir_hibp: bool = False, parent=None):
        super().__init__(parent)
        self._ruta        = ruta
        self._criterios   = criterios
        self._incluir_hibp = incluir_hibp

    def run(self) -> None:
        from batch.csv_processor import procesar_csv
        try:
            resultado = procesar_csv(
                self._ruta,
                self._criterios,
                incluir_hibp=self._incluir_hibp,
                callback=self._cb,
            )
        except Exception as exc:
            resultado = {
                "exitoso": False, "error": str(exc),
                "resultados": [], "omitidas": 0, "resumen": {},
            }
        self.completado.emit(resultado)

    def _cb(self, actual: int, total: int, usuario: str) -> None:
        self.progreso.emit(actual, total, usuario)
