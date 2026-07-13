"""
core/criteria.py
Define la política de contraseñas configurable y la verifica
contra un ResultadoAnalisis (definido en core/analyzer.py).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.analyzer import ResultadoAnalisis


@dataclass
class Criterios:
    """Política de autenticación configurable por el usuario."""
    longitud_minima:     int   = 12
    requiere_mayusculas: bool  = True
    requiere_minusculas: bool  = True
    requiere_digitos:    bool  = True
    requiere_simbolos:   bool  = True
    entropia_minima:     float = 40.0
    score_minimo:        int   = 3

    @classmethod
    def desde_config(cls, config: dict[str, str]) -> Criterios:
        """Construye un Criterios desde el dict de DatabaseManager.obtener_configuracion()."""
        return cls(
            longitud_minima     = int(config.get("longitud_minima",    12)),
            requiere_mayusculas = config.get("requiere_mayusculas", "true").lower() == "true",
            requiere_minusculas = config.get("requiere_minusculas", "true").lower() == "true",
            requiere_digitos    = config.get("requiere_digitos",    "true").lower() == "true",
            requiere_simbolos   = config.get("requiere_simbolos",   "true").lower() == "true",
            entropia_minima     = float(config.get("entropia_minima",  40.0)),
            score_minimo        = int(config.get("score_minimo",       3)),
        )

    @classmethod
    def predeterminada(cls) -> Criterios:
        return cls()

    def verificar(self, resultado: ResultadoAnalisis) -> tuple[bool, list[str]]:
        """
        Verifica si el resultado cumple la política.
        Devuelve (cumple: bool, incumplimientos: list[str]).
        Los mensajes son técnicos (lenguaje neutro); la UI los muestra o traduce.
        """
        inc: list[str] = []

        if resultado.longitud < self.longitud_minima:
            inc.append(
                f"Longitud mínima {self.longitud_minima} "
                f"(actual: {resultado.longitud})"
            )
        if self.requiere_mayusculas and not resultado.tiene_mayusculas:
            inc.append("Falta letra mayúscula")
        if self.requiere_minusculas and not resultado.tiene_minusculas:
            inc.append("Falta letra minúscula")
        if self.requiere_digitos and not resultado.tiene_digitos:
            inc.append("Falta dígito numérico")
        if self.requiere_simbolos and not resultado.tiene_simbolos:
            inc.append("Falta símbolo especial")
        if resultado.entropia < self.entropia_minima:
            inc.append(
                f"Entropía mínima {self.entropia_minima:.1f} bits "
                f"(actual: {resultado.entropia:.1f})"
            )
        if resultado.puntaje < self.score_minimo:
            inc.append(
                f"Score mínimo {self.score_minimo} "
                f"(actual: {resultado.puntaje})"
            )

        return len(inc) == 0, inc
