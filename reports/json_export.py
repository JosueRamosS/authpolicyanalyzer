"""
reports/json_export.py
Exportación de resultados a JSON estructurado.
Compatible con integración en otros sistemas.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from ui import i18n


def _meta() -> dict[str, str]:
    return {
        "app":                "AuthPolicyAnalyzer",
        "version":            "1.0.0",
        "fecha_exportacion":  datetime.now().isoformat(),
        "idioma":             i18n.idioma_activo(),
    }


def _limpiar_resultado(d: dict) -> dict:
    """
    Convierte tipos no serializables (como timedelta de zxcvbn)
    y elimina campos redundantes innecesarios para la exportación.
    """
    out: dict[str, Any] = {}
    for k, v in d.items():
        if hasattr(v, "total_seconds"):        # timedelta
            out[k] = str(v)
        elif isinstance(v, dict):
            out[k] = _limpiar_resultado(v)
        elif isinstance(v, list):
            out[k] = [
                _limpiar_resultado(i) if isinstance(i, dict) else i
                for i in v
            ]
        else:
            out[k] = v
    return out


# ------------------------------------------------------------------
# Exportar resultado individual
# ------------------------------------------------------------------

def exportar_resultado(resultado_dict: dict, ruta: str) -> None:
    """
    Exporta un único resultado de análisis a un archivo JSON.

    El archivo incluye:
      - Metadatos de la exportación (app, versión, fecha, idioma)
      - El resultado completo (hash, longitud, puntaje, etc.)

    La contraseña nunca se incluye; solo el hash SHA-256.
    """
    payload = {
        "meta":      _meta(),
        "resultado": _limpiar_resultado(resultado_dict),
    }
    _escribir_json(payload, ruta)


# ------------------------------------------------------------------
# Exportar lote completo
# ------------------------------------------------------------------

def exportar_lote(resultados: list[dict], ruta: str) -> None:
    """
    Exporta una lista de resultados de análisis (lote CSV) a JSON.

    Incluye:
      - Metadatos
      - Resumen estadístico del lote
      - Lista completa de resultados
    """
    resumen = _calcular_resumen(resultados)
    payload = {
        "meta":       _meta(),
        "resumen":    resumen,
        "resultados": [_limpiar_resultado(r) for r in resultados],
    }
    _escribir_json(payload, ruta)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _calcular_resumen(resultados: list[dict]) -> dict:
    total = len(resultados)
    por_categoria: dict[str, int] = {
        "muy_debil": 0, "debil": 0, "media": 0,
        "fuerte": 0, "muy_fuerte": 0,
    }
    comprometidas     = 0
    cumplen_politica  = 0
    en_diccionario    = 0

    for r in resultados:
        cat = r.get("categoria", "muy_debil")
        if cat in por_categoria:
            por_categoria[cat] += 1
        if r.get("en_filtraciones"):
            comprometidas += 1
        if r.get("cumple_politica"):
            cumplen_politica += 1
        if r.get("en_diccionario"):
            en_diccionario += 1

    return {
        "total":               total,
        "por_categoria":       por_categoria,
        "comprometidas":       comprometidas,
        "cumplen_politica":    cumplen_politica,
        "en_diccionario":      en_diccionario,
        "porcentaje_cumple":   round(cumplen_politica / total * 100, 1) if total else 0,
    }


def _escribir_json(payload: dict, ruta: str) -> None:
    directorio = os.path.dirname(ruta)
    if directorio:
        os.makedirs(directorio, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
