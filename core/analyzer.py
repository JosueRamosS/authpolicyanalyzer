"""
core/analyzer.py
Motor principal de análisis de contraseñas.
Combina entropía teórica, composición de caracteres y el score de zxcvbn
para producir un ResultadoAnalisis completo y serializable.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

try:
    from zxcvbn import zxcvbn as _zxcvbn_fn
    _ZXCVBN_OK = True
except ImportError:
    _ZXCVBN_OK = False

from core.criteria import Criterios

# ------------------------------------------------------------------
# Constantes de espacio de caracteres
# ------------------------------------------------------------------
_ESP_MINUSC  = 26   # a–z
_ESP_MAYUSC  = 26   # A–Z
_ESP_DIGITOS = 10   # 0–9
_ESP_SIMBOLOS = 33  # símbolos imprimibles ASCII (~33 comunes)

# Mapa score zxcvbn (0–4) → clave interna de categoría
CATEGORIAS: tuple[str, ...] = (
    "muy_debil", "debil", "media", "fuerte", "muy_fuerte"
)

# Clave i18n correspondiente (para que la UI la traduzca)
CLAVE_I18N: tuple[str, ...] = (
    "fortaleza_muy_debil",
    "fortaleza_debil",
    "fortaleza_media",
    "fortaleza_fuerte",
    "fortaleza_muy_fuerte",
)


# ------------------------------------------------------------------
# Estructura de datos del resultado
# ------------------------------------------------------------------

@dataclass
class ResultadoAnalisis:
    # ---- Identificación ----
    hash_sha256: str

    # ---- Métricas básicas ----
    longitud: int

    # ---- Composición ----
    tiene_minusculas: bool
    tiene_mayusculas: bool
    tiene_digitos:    bool
    tiene_simbolos:   bool

    # ---- Entropía ----
    espacio_caracteres: int
    entropia: float           # bits teóricos

    # ---- zxcvbn ----
    puntaje: int              # 0–4
    categoria: str            # 'muy_debil' | 'debil' | 'media' | 'fuerte' | 'muy_fuerte'
    tiempo_crackeo: dict      # crack_times_display de zxcvbn
    patrones_detectados: list[str]

    # ---- Ataque de diccionario ----
    en_diccionario:          bool
    variante_diccionario:    str   # variante que coincidió, '' si no
    esfuerzo_diccionario:    str   # descripción del esfuerzo estimado
    total_variantes:         int  = 0

    # ---- HIBP (se rellena externamente) ----
    en_filtraciones: bool = False
    veces_filtrada:  int  = 0
    hibp_disponible: bool = False

    # ---- Política ----
    cumple_politica: bool      = False
    incumplimientos: list[str] = field(default_factory=list)

    # ---- Salida final ----
    hallazgos:       list[str] = field(default_factory=list)
    recomendaciones: list[str] = field(default_factory=list)

    # ---- Metadatos ----
    fecha: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convierte a dict plano (listo para guardar en BD o exportar a JSON)."""
        return asdict(self)

    @property
    def clave_i18n(self) -> str:
        """Devuelve la clave de i18n correspondiente al nivel de fortaleza."""
        idx = max(0, min(self.puntaje, 4))
        return CLAVE_I18N[idx]

    @property
    def porcentaje_barra(self) -> int:
        """Porcentaje para la barra de progreso (0–100), suavizado por entropía."""
        base  = (self.puntaje / 4) * 100
        bonus = min(self.entropia / 100, 1.0) * 10   # hasta +10 pts por entropía alta
        return min(int(base + bonus), 100)


# ------------------------------------------------------------------
# Funciones de cálculo
# ------------------------------------------------------------------

def calcular_espacio_caracteres(password: str) -> int:
    """Tamaño del espacio de búsqueda según los tipos de carácter presentes."""
    espacio = 0
    if any(c.islower() for c in password):
        espacio += _ESP_MINUSC
    if any(c.isupper() for c in password):
        espacio += _ESP_MAYUSC
    if any(c.isdigit() for c in password):
        espacio += _ESP_DIGITOS
    if any(not c.isalnum() for c in password):
        espacio += _ESP_SIMBOLOS
    return max(espacio, 1)


def calcular_entropia(password: str) -> float:
    """Entropía teórica en bits = len × log₂(espacio de caracteres)."""
    espacio = calcular_espacio_caracteres(password)
    return len(password) * math.log2(espacio)


def _safe_zxcvbn(password: str) -> dict[str, Any]:
    if not _ZXCVBN_OK:
        return {"score": 0, "crack_times_display": {}, "sequence": [], "feedback": {}}
    try:
        return _zxcvbn_fn(password)  # type: ignore[misc]
    except Exception:
        return {"score": 0, "crack_times_display": {}, "sequence": [], "feedback": {}}


def _hallazgos_tecnicos(r: ResultadoAnalisis) -> list[str]:
    """
    Genera una lista de hallazgos objetivos (hechos, no sugerencias).
    Se guardan en BD y se muestran en el reporte PDF.
    """
    h: list[str] = []
    if r.longitud < 8:
        h.append(f"Contraseña muy corta ({r.longitud} caracteres)")
    if not r.tiene_mayusculas:
        h.append("Sin letras mayúsculas")
    if not r.tiene_minusculas:
        h.append("Sin letras minúsculas")
    if not r.tiene_digitos:
        h.append("Sin dígitos numéricos")
    if not r.tiene_simbolos:
        h.append("Sin símbolos especiales")
    if r.en_diccionario:
        h.append(
            f"Encontrada en diccionario "
            f"(variante: {r.variante_diccionario!r}, "
            f"esfuerzo: {r.esfuerzo_diccionario})"
        )
    if r.en_filtraciones:
        h.append(f"Comprometida {r.veces_filtrada:,} veces en filtraciones")
    if r.patrones_detectados:
        h.append(f"Patrones: {', '.join(dict.fromkeys(r.patrones_detectados))}")
    if r.entropia < 28:
        h.append(f"Entropía muy baja: {r.entropia:.1f} bits")
    if not r.cumple_politica:
        h.append("No cumple la política de seguridad configurada")
    return h


# ------------------------------------------------------------------
# Función principal
# ------------------------------------------------------------------

def analizar(
    password: str,
    criterios: Criterios | None = None,
    resultado_diccionario: dict | None = None,
) -> ResultadoAnalisis:
    """
    Analiza una contraseña y devuelve un ResultadoAnalisis.

    Pasos:
      1. Composición de caracteres
      2. Entropía teórica
      3. zxcvbn (score + crack_times + patrones)
      4. Ataque de diccionario (si se provee resultado_diccionario)
      5. Verificación de política (criterios)
      6. Hallazgos técnicos

    HIBP y las recomendaciones finales se añaden externamente
    (son operaciones de red / dependientes del idioma activo).
    """
    if criterios is None:
        criterios = Criterios()

    # 1. Hash seguro — la contraseña NUNCA se almacena
    sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # 2. Composición
    tiene_min = any(c.islower() for c in password)
    tiene_may = any(c.isupper() for c in password)
    tiene_dig = any(c.isdigit() for c in password)
    tiene_sim = any(not c.isalnum() for c in password)

    # 3. Entropía
    espacio  = calcular_espacio_caracteres(password)
    entropia = round(calcular_entropia(password), 2)

    # 4. zxcvbn
    z         = _safe_zxcvbn(password)
    puntaje   = int(z.get("score", 0))
    categoria = CATEGORIAS[max(0, min(puntaje, 4))]
    crack_t   = z.get("crack_times_display", {})
    patrones  = [
        s.get("pattern", "desconocido")
        for s in z.get("sequence", [])
        if s.get("pattern") not in (None, "bruteforce")
    ]

    # 5. Diccionario
    en_dic  = False
    variante = ""
    esfuerzo = ""
    total_variantes = 0
    if resultado_diccionario:
        en_dic   = bool(resultado_diccionario.get("encontrada", False))
        variante = str(resultado_diccionario.get("variante",   ""))
        esfuerzo = str(resultado_diccionario.get("esfuerzo",   ""))
        total_variantes = int(resultado_diccionario.get("total_variantes_probadas", 0))

    # Construcción del resultado
    resultado = ResultadoAnalisis(
        hash_sha256          = sha256,
        longitud             = len(password),
        tiene_minusculas     = tiene_min,
        tiene_mayusculas     = tiene_may,
        tiene_digitos        = tiene_dig,
        tiene_simbolos       = tiene_sim,
        espacio_caracteres   = espacio,
        entropia             = entropia,
        puntaje              = puntaje,
        categoria            = categoria,
        tiempo_crackeo       = dict(crack_t),
        patrones_detectados  = patrones,
        en_diccionario       = en_dic,
        variante_diccionario = variante,
        esfuerzo_diccionario = esfuerzo,
        total_variantes      = total_variantes,
    )

    # 6. Política
    cumple, incumplimientos = criterios.verificar(resultado)
    resultado.cumple_politica = cumple
    resultado.incumplimientos = incumplimientos

    # 7. Hallazgos técnicos
    resultado.hallazgos = _hallazgos_tecnicos(resultado)

    return resultado
