"""
core/dictionary_attack.py
Simula un ataque de diccionario con variaciones comunes:
  - coincidencia directa
  - cambios de mayúsculas/minúsculas
  - reversión de leetspeak (@ → a, 3 → e, 0 → o …)
  - eliminación de prefijos/sufijos numéricos o simbólicos

No genera variantes del diccionario (sería exponencial);
en cambio, aplica transformaciones INVERSAS a la contraseña
y comprueba si el resultado existe en el diccionario.
"""
from __future__ import annotations

import os
import re

_RUTA_DICCIONARIO = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "common_passwords.txt")
)

# Mapeo leetspeak inverso — un solo carácter por sustitución
_LEET_INV: dict[str, str] = {
    "@": "a", "4": "a",
    "3": "e",
    "1": "i", "!": "i",
    "0": "o",
    "$": "s", "5": "s",
    "7": "t",
    "8": "b",
    "9": "g",
}

_RX_SUFIJO  = re.compile(r"[\d!@#$%^&*_\-]+$")
_RX_PREFIJO = re.compile(r"^[\d!@#$%^&*_\-]+")

_cache_dic: set[str] | None = None


def _cargar_diccionario() -> set[str]:
    global _cache_dic
    if _cache_dic is not None:
        return _cache_dic
    try:
        with open(_RUTA_DICCIONARIO, encoding="utf-8") as f:
            _cache_dic = {l.strip().lower() for l in f if l.strip()}
    except FileNotFoundError:
        _cache_dic = set()
    return _cache_dic


def _desleet(texto: str) -> str:
    return "".join(_LEET_INV.get(c, c) for c in texto)


def _candidatos(password: str) -> list[tuple[str, str, str]]:
    """
    Genera variantes de la contraseña para comparar contra el diccionario.
    Cada elemento: (variante_en_minúsculas, descripción, esfuerzo_estimado).
    """
    p  = password
    pl = p.lower()

    raw: list[tuple[str, str, str]] = [
        (p,                   "directo",                "Inmediato"),
        (pl,                  "minúsculas",             "Trivial"),
        (p.upper(),           "mayúsculas",             "Trivial"),
        (pl.capitalize(),     "primera mayúscula",      "Muy bajo"),
        (_desleet(pl),        "leetspeak inverso",      "Bajo"),
        (_desleet(p).lower(), "leetspeak+minúsculas",   "Bajo"),
    ]

    # Sin sufijo numérico/simbólico
    sin_suf = _RX_SUFIJO.sub("", pl)
    if sin_suf and sin_suf != pl:
        raw.append((sin_suf, "sin sufijo", "Bajo"))
        raw.append((_desleet(sin_suf), "leetspeak+sin sufijo", "Bajo"))

    # Sin prefijo numérico/simbólico
    sin_pre = _RX_PREFIJO.sub("", pl)
    if sin_pre and sin_pre != pl:
        raw.append((sin_pre, "sin prefijo", "Bajo"))

    # Sin prefijo ni sufijo
    if sin_suf:
        sin_ambos = _RX_PREFIJO.sub("", sin_suf)
        if sin_ambos and sin_ambos not in {pl, sin_suf, sin_pre}:
            raw.append((sin_ambos, "sin prefijo+sufijo", "Bajo"))

    # Deduplicar manteniendo orden de prioridad
    seen: set[str] = set()
    result: list[tuple[str, str, str]] = []
    for variante, desc, esf in raw:
        clave = variante.lower()
        if clave and clave not in seen:
            seen.add(clave)
            result.append((clave, desc, esf))
    return result


def simular_ataque(password: str) -> dict:
    """
    Comprueba si la contraseña (o una derivación común) está en el diccionario.

    Devuelve:
        {
            'encontrada': bool,
            'variante':   str,   # variante que coincidió
            'descripcion': str,  # tipo de transformación
            'esfuerzo':   str,   # estimación del esfuerzo del atacante
            'total_variantes_probadas': int,
        }
    """
    dic      = _cargar_diccionario()
    variantes = _candidatos(password)

    if not dic:
        return {
            "encontrada": False, "variante": "", "descripcion": "",
            "esfuerzo": "", "total_variantes_probadas": 0,
        }

    for clave, desc, esf in variantes:
        if clave in dic:
            return {
                "encontrada": True,
                "variante":   clave,
                "descripcion": desc,
                "esfuerzo":   esf,
                "total_variantes_probadas": len(variantes),
            }

    return {
        "encontrada": False, "variante": "", "descripcion": "",
        "esfuerzo": "", "total_variantes_probadas": len(variantes),
    }
