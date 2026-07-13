"""
services/hibp.py
Verificación de contraseñas comprometidas usando la API Pwned Passwords
de Have I Been Pwned (HIBP) con k-anonymity.

Protocolo k-anonymity:
  1. Se calcula el SHA-1 de la contraseña (local).
  2. Se envían SOLO los primeros 5 caracteres (prefijo) a la API.
  3. La API devuelve todos los sufijos que empiezan con ese prefijo.
  4. La comparación se hace localmente: la contraseña y el hash completo
     NUNCA salen del sistema.

Si no hay conexión a internet, la función retorna 'disponible=False'
sin lanzar excepciones (degradación elegante).
"""
from __future__ import annotations

import hashlib

try:
    import requests
    from requests.exceptions import RequestException, Timeout
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

_HIBP_URL = "https://api.pwnedpasswords.com/range/{prefix}"
_TIMEOUT  = 5.0  # segundos

_HEADERS = {
    "User-Agent": "AuthPolicyAnalyzer/1.0 (academic)",
    "Add-Padding": "true",   # previene análisis de tráfico por tamaño de respuesta
}

# Caché en memoria por sesión: prefijo → texto de respuesta HIBP
# Evita peticiones duplicadas en análisis de lotes.
_cache: dict[str, str] = {}


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _sha1_split(password: str) -> tuple[str, str]:
    """Devuelve (prefijo_5_chars_UPPER, sufijo_UPPER) del hash SHA-1."""
    h = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    return h[:5], h[5:]


def _fetch_hibp(prefix: str, timeout: float) -> str | None:
    """
    Descarga la lista de sufijos para el prefijo dado.
    Devuelve el texto raw o None si hay error de red.
    """
    if not _REQUESTS_OK:
        return None
    try:
        resp = requests.get(
            _HIBP_URL.format(prefix=prefix),
            headers=_HEADERS,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def _buscar_en_respuesta(texto: str, sufijo: str) -> int:
    """Busca el sufijo en el texto de respuesta. Devuelve el conteo o 0."""
    for linea in texto.splitlines():
        partes = linea.strip().split(":", 1)
        if len(partes) == 2 and partes[0] == sufijo:
            try:
                return int(partes[1])
            except ValueError:
                return 0
    return 0


# ------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------

def verificar(password: str, timeout: float = _TIMEOUT) -> dict:
    """
    Comprueba si la contraseña aparece en filtraciones conocidas.

    Devuelve:
        {
            'encontrada':     bool,
            'veces_filtrada': int,   # 0 si no encontrada
            'disponible':     bool,  # False si no hay conexión / error
        }
    """
    prefix, sufijo = _sha1_split(password)

    if prefix not in _cache:
        texto = _fetch_hibp(prefix, timeout)
        if texto is None:
            return {"encontrada": False, "veces_filtrada": 0, "disponible": False}
        _cache[prefix] = texto

    conteo = _buscar_en_respuesta(_cache[prefix], sufijo)

    if conteo > 0:
        return {"encontrada": True,  "veces_filtrada": conteo, "disponible": True}
    return     {"encontrada": False, "veces_filtrada": 0,      "disponible": True}


def limpiar_cache() -> None:
    """Vacía la caché de prefijos (útil al iniciar un nuevo lote)."""
    _cache.clear()
