"""
batch/csv_processor.py
Procesamiento en lote de contraseñas desde un archivo CSV.

Formato esperado del CSV:
    usuario,contrasena
    alice,MiContrasena1!
    bob,qwerty123

  - La primera fila puede ser cabecera (se detecta automáticamente).
  - Delimitador: coma (,) o punto y coma (;) — se detecta automáticamente.
  - Codificación: UTF-8 o UTF-8 con BOM.
  - Columnas: dos mínimas (usuario, contraseña). Se ignoran columnas adicionales.
  - Máximo recomendado: 10 000 filas (sin límite técnico).

Privacidad: las contraseñas del CSV NUNCA se guardan; el resultado
contiene solo hashes SHA-256, puntajes y metadatos.
"""
from __future__ import annotations

import csv
import io
import os
from typing import Callable

from core.analyzer          import analizar, ResultadoAnalisis
from core.criteria          import Criterios
from core.dictionary_attack import simular_ataque
from core.recommendations   import generar_recomendaciones
from services               import hibp as _hibp


# Nombres de columna aceptados (en minúsculas)
_COLS_USUARIO    = {"usuario", "user", "username", "nombre", "name"}
_COLS_CONTRASENA = {"contrasena", "contraseña", "password", "pass", "pwd", "clave"}


# ------------------------------------------------------------------
# Detección de formato
# ------------------------------------------------------------------

def _detectar_dialecto(muestra: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(muestra, delimiters=",;|\t")
    except csv.Error:
        return csv.excel   # fallback: coma estándar


def _tiene_cabecera(muestra: str, dialecto) -> bool:
    try:
        return csv.Sniffer().has_header(muestra)
    except csv.Error:
        return False


def _resolver_indices(cabecera: list[str]) -> tuple[int, int] | None:
    """
    Devuelve (idx_usuario, idx_contrasena) a partir de los nombres de columna.
    Devuelve None si no se pueden identificar.
    """
    lower = [c.strip().lower() for c in cabecera]
    idx_u = next((i for i, c in enumerate(lower) if c in _COLS_USUARIO),    None)
    idx_p = next((i for i, c in enumerate(lower) if c in _COLS_CONTRASENA), None)
    if idx_u is None or idx_p is None:
        return None
    return idx_u, idx_p


# ------------------------------------------------------------------
# Procesamiento principal
# ------------------------------------------------------------------

def procesar_csv(
    ruta: str,
    criterios: Criterios | None = None,
    incluir_hibp: bool = True,
    callback: Callable[[int, int, str], None] | None = None,
) -> dict:
    """
    Procesa un archivo CSV y evalúa cada contraseña.

    Args:
        ruta:          Ruta al archivo CSV.
        criterios:     Política de evaluación (usa predeterminados si es None).
        incluir_hibp:  Si True, consulta HIBP para cada contraseña.
        callback:      Función(actual, total, usuario) llamada tras cada fila.

    Devuelve:
        {
            'exitoso':    bool,
            'error':      str,           # mensaje si no exitoso
            'resultados': list[dict],    # uno por fila válida
            'omitidas':   int,           # filas con error de formato
            'resumen': {
                'total': int,
                'muy_debil': int, 'debil': int, 'media': int,
                'fuerte': int, 'muy_fuerte': int,
                'comprometidas': int, 'cumplen_politica': int,
                'en_diccionario': int,
            }
        }
    """
    if criterios is None:
        criterios = Criterios()

    # --- Leer archivo ---
    try:
        with open(ruta, encoding="utf-8-sig") as f:
            contenido = f.read()
    except FileNotFoundError:
        return _error(f"Archivo no encontrado: {ruta}")
    except Exception as exc:
        return _error(f"No se pudo leer el archivo: {exc}")

    if not contenido.strip():
        return _error("El archivo CSV está vacío.")

    muestra   = contenido[:4096]
    dialecto  = _detectar_dialecto(muestra)
    tiene_hdr = _tiene_cabecera(muestra, dialecto)

    reader = csv.reader(io.StringIO(contenido), dialecto)
    filas  = list(reader)
    if not filas:
        return _error("El archivo CSV no contiene filas.")

    # Determinar índices de columna: primero intenta por nombre, luego posicional
    indices = _resolver_indices(filas[0])
    if indices is not None:
        # La primera fila es una cabecera reconocida
        idx_u, idx_p = indices
        datos = filas[1:]
    elif len(filas[0]) >= 2:
        # Sin cabecera reconocible: columna 0 = usuario, columna 1 = contraseña
        idx_u, idx_p = 0, 1
        datos = filas
    else:
        return _error(
            "El CSV debe tener al menos dos columnas: usuario,contrasena"
        )

    # --- Evaluar cada fila ---
    _hibp.limpiar_cache()

    resultados: list[dict] = []
    omitidas  = 0
    total     = len(datos)

    for i, fila in enumerate(datos):
        try:
            usuario   = fila[idx_u].strip() if len(fila) > idx_u else f"fila_{i+1}"
            contrasena = fila[idx_p].strip() if len(fila) > idx_p else ""

            if not contrasena:
                omitidas += 1
                continue

            # Pipeline de análisis
            dic  = simular_ataque(contrasena)
            res  = analizar(contrasena, criterios, dic)

            if incluir_hibp:
                hibp_res = _hibp.verificar(contrasena)
                res.en_filtraciones = hibp_res["encontrada"]
                res.veces_filtrada  = hibp_res["veces_filtrada"]
                res.hibp_disponible = hibp_res["disponible"]

            res.recomendaciones = generar_recomendaciones(res)

            d = res.to_dict()
            d["usuario"] = usuario   # añadir campo identificador (no la contraseña)
            resultados.append(d)

        except Exception:
            omitidas += 1
            continue

        if callback:
            try:
                callback(i + 1, total, usuario)
            except Exception:
                pass

    if not resultados:
        return _error("No se pudo procesar ninguna fila del CSV.")

    return {
        "exitoso":    True,
        "error":      "",
        "resultados": resultados,
        "omitidas":   omitidas,
        "resumen":    _calcular_resumen(resultados),
    }


# ------------------------------------------------------------------
# Validación sin procesamiento
# ------------------------------------------------------------------

def validar_csv(ruta: str) -> dict:
    """
    Valida el formato del CSV sin evaluar las contraseñas.
    Rápido: solo lee las primeras filas.

    Devuelve:
        {
            'valido':           bool,
            'error':            str,
            'total_filas':      int,
            'tiene_cabecera':   bool,
            'columnas':         list[str],
            'muestra':          list[dict],  # primeras 3 filas como [{usuario, contrasena}]
        }
    """
    try:
        with open(ruta, encoding="utf-8-sig") as f:
            contenido = f.read()
    except Exception as exc:
        return {"valido": False, "error": str(exc)}

    muestra_txt = contenido[:4096]
    dialecto    = _detectar_dialecto(muestra_txt)
    tiene_hdr   = _tiene_cabecera(muestra_txt, dialecto)

    reader = csv.reader(io.StringIO(contenido), dialecto)
    filas  = list(reader)

    if not filas:
        return {"valido": False, "error": "El archivo está vacío."}

    indices = _resolver_indices(filas[0])
    if indices is not None:
        idx_u, idx_p = indices
        datos    = filas[1:]
        columnas = filas[0]
        tiene_hdr = True
    elif len(filas[0]) >= 2:
        idx_u, idx_p = 0, 1
        datos    = filas
        columnas = []
        tiene_hdr = False
    else:
        return {"valido": False, "error": "Se necesitan al menos 2 columnas."}

    muestra = [
        {
            "usuario":    f[idx_u] if len(f) > idx_u else "",
            "contrasena": f"{'*' * len(f[idx_p])}" if len(f) > idx_p else "",
        }
        for f in datos[:3]
    ]

    return {
        "valido":         True,
        "error":          "",
        "total_filas":    len(datos),
        "tiene_cabecera": tiene_hdr,
        "columnas":       columnas,
        "muestra":        muestra,
    }


# ------------------------------------------------------------------
# Helpers internos
# ------------------------------------------------------------------

def _error(msg: str) -> dict:
    return {
        "exitoso":    False,
        "error":      msg,
        "resultados": [],
        "omitidas":   0,
        "resumen":    {},
    }


def _calcular_resumen(resultados: list[dict]) -> dict:
    conteo: dict[str, int] = {
        "muy_debil": 0, "debil": 0, "media": 0,
        "fuerte": 0, "muy_fuerte": 0,
    }
    comprometidas, politica, diccionario = 0, 0, 0
    for r in resultados:
        cat = r.get("categoria", "muy_debil")
        if cat in conteo:
            conteo[cat] += 1
        if r.get("en_filtraciones"):
            comprometidas += 1
        if r.get("cumple_politica"):
            politica += 1
        if r.get("en_diccionario"):
            diccionario += 1
    total = len(resultados)
    return {
        "total":            total,
        **conteo,
        "comprometidas":    comprometidas,
        "cumplen_politica": politica,
        "en_diccionario":   diccionario,
        "porcentaje_cumple": round(politica / total * 100, 1) if total else 0.0,
    }
