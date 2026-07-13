"""
core/recommendations.py
Motor de reglas que genera recomendaciones de seguridad a partir
de un ResultadoAnalisis.  Las recomendaciones se producen en el
idioma activo usando ui.i18n; el módulo core no cambia el estado
de i18n, solo lo lee.

Orden de severidad: CRÍTICO → ALTO → MEDIO → BAJO → GENERAL
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.analyzer import ResultadoAnalisis

from ui import i18n


def generar_recomendaciones(resultado: ResultadoAnalisis) -> list[str]:
    """
    Aplica el motor de reglas y devuelve una lista ordenada de
    recomendaciones accionables en el idioma activo.
    """
    t    = i18n.t
    recs: list[str] = []

    # ------------------------------------------------------------------
    # CRÍTICO — contraseña comprometida en filtraciones
    # ------------------------------------------------------------------
    if resultado.en_filtraciones and resultado.hibp_disponible:
        recs.append(t("rec_en_filtraciones", n=f"{resultado.veces_filtrada:,}"))

    # ------------------------------------------------------------------
    # ALTO — encontrada en diccionario de contraseñas comunes
    # ------------------------------------------------------------------
    if resultado.en_diccionario:
        recs.append(t("rec_no_diccionario"))
        # Subanotación si fue un matcheo por leetspeak
        if resultado.esfuerzo_diccionario.lower() in ("bajo", "low") and \
           "leet" in resultado.variante_diccionario.lower() or \
           "leet" in resultado.esfuerzo_diccionario.lower():
            recs.append(t("rec_leetspeak_simple"))

    # ------------------------------------------------------------------
    # ALTO — score zxcvbn muy bajo
    # ------------------------------------------------------------------
    if resultado.puntaje <= 1:
        recs.append(t("rec_score_bajo"))

    # ------------------------------------------------------------------
    # MEDIO — longitud insuficiente
    # ------------------------------------------------------------------
    longitud_objetivo = 16 if resultado.longitud < 8 else 12
    if resultado.longitud < longitud_objetivo:
        recs.append(t("rec_aumentar_longitud", n=longitud_objetivo))

    # ------------------------------------------------------------------
    # MEDIO — composición de caracteres
    # ------------------------------------------------------------------
    if not resultado.tiene_mayusculas:
        recs.append(t("rec_agregar_mayusculas"))
    if not resultado.tiene_minusculas:
        recs.append(t("rec_agregar_minusculas"))
    if not resultado.tiene_digitos:
        recs.append(t("rec_agregar_digitos"))
    if not resultado.tiene_simbolos:
        recs.append(t("rec_agregar_simbolos"))

    # ------------------------------------------------------------------
    # MEDIO — entropía baja
    # ------------------------------------------------------------------
    if resultado.entropia < 40.0:
        recs.append(t("rec_baja_entropia", entropia=resultado.entropia))

    # ------------------------------------------------------------------
    # BAJO — leetspeak sin haberse detectado ya por diccionario
    # ------------------------------------------------------------------
    if not resultado.en_diccionario:
        descripcion = resultado.esfuerzo_diccionario.lower()
        if "leet" in descripcion:
            recs.append(t("rec_leetspeak_simple"))

    # ------------------------------------------------------------------
    # GENERAL — siempre al final
    # ------------------------------------------------------------------
    if not recs:
        recs.append(t("rec_sin_problemas"))
    else:
        recs.append(t("rec_usar_gestor"))

    # Eliminar duplicados preservando el orden
    vistos: set[str] = set()
    resultado_final: list[str] = []
    for r in recs:
        if r not in vistos:
            vistos.add(r)
            resultado_final.append(r)

    return resultado_final
