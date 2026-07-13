"""
ui/i18n.py
Módulo de internacionalización (ES / EN).
Centraliza todos los textos visibles de la aplicación.
En Fase 4 se añaden los textos del resto de módulos de la interfaz.
"""
from __future__ import annotations

IDIOMAS: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------------
    # ESPAÑOL
    # ------------------------------------------------------------------
    "es": {
        # App
        "app_titulo":    "AuthPolicyAnalyzer",
        "app_subtitulo": "Analizador de Fortaleza de Políticas de Autenticación",
        "version":       "v1.0.0",
        "idioma_actual": "ES",

        # Pestañas
        "tab_analizar":  "Analizar",
        "tab_lote":      "Lote CSV",
        "tab_historial": "Historial",
        "tab_config":    "Configuración",

        # Status bar
        "listo":         "Listo",
        "db_ok":         "Base de datos inicializada correctamente",
        "idioma_cambiado": "Idioma cambiado a: {idioma}",

        # Tab Analizar
        "contrasena_a_evaluar": "Contraseña a Evaluar",
        "placeholder_input":    "Ingresa la contraseña a analizar...",
        "btn_analizar":         "ANALIZAR",
        "btn_ver":              "Ver",
        "btn_ocultar":          "Ocultar",
        "btn_exportar_pdf":     "Exportar PDF",
        "btn_exportar_json":    "Exportar JSON",
        "resultados":           "Resultados del Análisis",
        "placeholder_resultados": (
            "Ingresa una contraseña y presiona ANALIZAR para ver los resultados.\n\n"
            "  —  Fortaleza y puntaje (0–4)\n"
            "  —  Entropía calculada\n"
            "  —  Verificación contra filtraciones (HIBP)\n"
            "  —  Simulación de ataque de diccionario\n"
            "  —  Recomendaciones detalladas"
        ),

        "detalles":             "Detalles del Análisis",

        # Fortaleza
        "fortaleza_muy_debil":  "Muy débil",
        "fortaleza_debil":      "Débil",
        "fortaleza_media":      "Media",
        "fortaleza_fuerte":     "Fuerte",
        "fortaleza_muy_fuerte": "Muy fuerte",

        # Campos de resultado
        "longitud":         "Longitud",
        "caracteres":       "caracteres",
        "entropia":         "Entropía",
        "bits":             "bits",
        "puntaje":          "Puntaje zxcvbn",
        "filtraciones":     "Filtraciones (HIBP)",
        "veces_filtrada":   "veces en filtraciones",
        "no_filtrada":      "No encontrada en filtraciones",
        "hibp_error":       "No disponible (sin conexión)",
        "diccionario":      "Ataque de diccionario",
        "encontrada_dic":   "Encontrada en diccionario",
        "no_encontrada_dic":"No encontrada en diccionario",
        "cumple_politica":  "Cumple política",
        "no_cumple":        "No cumple política",
        "si_cumple":        "Cumple la política configurada",

        # Tiempo de crackeo
        "tiempo_crackeo":        "Tiempo estimado de crackeo",
        "online_throttling":     "Ataque en línea (limitado)",
        "online_no_throttling":  "Ataque en línea (sin límite)",
        "offline_slow_hash":     "Offline — hash lento",
        "offline_fast_hash":     "Offline — hash rápido",

        # Recomendaciones
        "recomendaciones": "Recomendaciones",
        "sin_hallazgos":   "Sin hallazgos críticos.",

        # Tab Lote CSV
        "lote_titulo":      "Evaluación en Lote por CSV",
        "lote_descripcion": (
            "Carga un archivo CSV con contraseñas para evaluarlas en masa.\n"
            "Formato esperado:  usuario,contrasena"
        ),
        "btn_cargar_csv":   "Cargar archivo CSV",
        "btn_exportar_lote": "Exportar resultados",
        "procesando":       "Procesando...",
        "lote_completo":    "Lote completado: {total} contraseñas evaluadas.",
        "csv_error_formato": "El archivo CSV no tiene el formato esperado.",
        "csv_col_usuario":  "Usuario",
        "csv_col_contrasena": "Contraseña (hash)",
        "csv_col_puntaje":  "Puntaje",
        "csv_col_categoria": "Categoría",
        "csv_col_entropia": "Entropía (bits)",
        "csv_col_filtrada": "En filtraciones",
        "csv_col_politica": "Cumple política",

        # Tab Historial
        "historial_titulo": "Historial de Evaluaciones",
        "historial_vacio":  "No hay evaluaciones registradas aún.",
        "btn_borrar_todo":  "Borrar historial",
        "btn_borrar_sel":   "Borrar seleccionado",
        "confirmar_borrar": "¿Confirmar eliminación?",
        "confirmar_borrar_todo": "¿Deseas borrar todo el historial? Esta acción no se puede deshacer.",
        "hist_col_id":      "ID",
        "hist_col_fecha":   "Fecha",
        "hist_col_longitud": "Long.",
        "hist_col_puntaje": "Puntaje",
        "hist_col_categoria": "Categoría",
        "hist_col_entropia": "Entropía",
        "hist_col_filtrada": "Filtrada",
        "hist_col_politica": "Política",
        "total_registros":  "Total: {n} registros",

        # Tab Configuración
        "config_titulo":       "Configuración de Políticas",
        "config_longitud":     "Longitud mínima (caracteres)",
        "config_mayusculas":   "Requiere mayúsculas",
        "config_minusculas":   "Requiere minúsculas",
        "config_digitos":      "Requiere dígitos",
        "config_simbolos":     "Requiere símbolos",
        "config_entropia":     "Entropía mínima (bits)",
        "config_score":        "Score mínimo aceptable (0–4)",
        "config_idioma":       "Idioma de la interfaz",
        "btn_guardar_config":  "Guardar configuración",
        "btn_restaurar":       "Restaurar predeterminados",
        "config_guardada":     "Configuración guardada correctamente.",
        "config_restaurada":   "Configuración restaurada a valores predeterminados.",

        # PDF
        "pdf_titulo":          "Reporte de Evaluación de Contraseña",
        "pdf_fecha":           "Fecha",
        "pdf_resumen":         "Resumen",
        "pdf_contrasena":      "Contraseña evaluada",
        "pdf_longitud":        "Longitud",
        "pdf_mascara":         "(longitud: {n} caracteres)",
        "pdf_hallazgos":       "Hallazgos",
        "pdf_recomendaciones": "Recomendaciones",
        "pdf_generado":        "Reporte PDF generado: {ruta}",
        "pdf_error":           "Error al generar el PDF: {error}",

        # Errores generales
        "error_titulo":        "Error",
        "error_conexion":      "Sin conexión a internet.",
        "error_archivo":       "No se pudo abrir el archivo.",
        "error_generico":      "Ocurrió un error inesperado.",
        "advertencia":         "Advertencia",
        "informacion":         "Información",

        # Recomendaciones (generadas por core/recommendations.py)
        "rec_en_filtraciones":   "CRÍTICO: Esta contraseña aparece {n} veces en bases de datos de filtraciones públicas. Cámbiala inmediatamente y no la reutilices en ningún otro sitio.",
        "rec_no_diccionario":    "Evita contraseñas de diccionario o combinaciones predecibles. Los atacantes las prueban exhaustivamente en las primeras fases de un ataque.",
        "rec_score_bajo":        "El puntaje de seguridad es muy bajo. Considera usar una frase de contraseña (passphrase): 4 o 5 palabras aleatorias unidas son más seguras y fáciles de recordar.",
        "rec_aumentar_longitud": "Aumenta la longitud a al menos {n} caracteres. Cada carácter adicional multiplica el tiempo de crackeo.",
        "rec_agregar_mayusculas":"Incluye al menos una letra mayúscula (A–Z) para ampliar el espacio de caracteres.",
        "rec_agregar_minusculas":"Incluye letras minúsculas (a–z).",
        "rec_agregar_digitos":   "Añade al menos un dígito (0–9).",
        "rec_agregar_simbolos":  "Añade símbolos especiales como @, #, $, !, % o ^ para aumentar significativamente la complejidad.",
        "rec_baja_entropia":     "La entropía calculada ({entropia:.1f} bits) es insuficiente. Usa una combinación más diversa de tipos de carácter o una contraseña más larga.",
        "rec_leetspeak_simple":  "Las sustituciones simples de leetspeak (a→@, e→3, o→0) son ampliamente conocidas y están incluidas en los diccionarios de ataque modernos. No añaden seguridad real.",
        "rec_sin_problemas":     "¡Excelente! No se detectaron problemas significativos. Recuerda usar contraseñas únicas para cada servicio y activar la autenticación en dos factores cuando sea posible.",
        "rec_usar_gestor":       "Usa un gestor de contraseñas (Bitwarden, KeePass, 1Password) para generar y almacenar contraseñas largas, únicas y aleatorias en cada servicio.",
    },

    # ------------------------------------------------------------------
    # ENGLISH
    # ------------------------------------------------------------------
    "en": {
        # App
        "app_titulo":    "AuthPolicyAnalyzer",
        "app_subtitulo": "Authentication Policy Strength Analyzer",
        "version":       "v1.0.0",
        "idioma_actual": "EN",

        # Tabs
        "tab_analizar":  "Analyze",
        "tab_lote":      "CSV Batch",
        "tab_historial": "History",
        "tab_config":    "Settings",

        # Status bar
        "listo":         "Ready",
        "db_ok":         "Database initialized successfully",
        "idioma_cambiado": "Language changed to: {idioma}",

        # Tab Analyze
        "contrasena_a_evaluar": "Password to Evaluate",
        "placeholder_input":    "Enter the password to analyze...",
        "btn_analizar":         "ANALYZE",
        "btn_ver":              "Show",
        "btn_ocultar":          "Hide",
        "btn_exportar_pdf":     "Export PDF",
        "btn_exportar_json":    "Export JSON",
        "resultados":           "Analysis Results",
        "placeholder_resultados": (
            "Enter a password and press ANALYZE to see the results.\n\n"
            "  —  Strength and score (0–4)\n"
            "  —  Calculated entropy\n"
            "  —  Breach check (HIBP)\n"
            "  —  Dictionary attack simulation\n"
            "  —  Detailed recommendations"
        ),

        "detalles":             "Analysis Details",

        # Strength
        "fortaleza_muy_debil":  "Very weak",
        "fortaleza_debil":      "Weak",
        "fortaleza_media":      "Medium",
        "fortaleza_fuerte":     "Strong",
        "fortaleza_muy_fuerte": "Very strong",

        # Result fields
        "longitud":         "Length",
        "caracteres":       "characters",
        "entropia":         "Entropy",
        "bits":             "bits",
        "puntaje":          "zxcvbn score",
        "filtraciones":     "Breaches (HIBP)",
        "veces_filtrada":   "times in breaches",
        "no_filtrada":      "Not found in breaches",
        "hibp_error":       "Unavailable (no connection)",
        "diccionario":      "Dictionary attack",
        "encontrada_dic":   "Found in dictionary",
        "no_encontrada_dic":"Not found in dictionary",
        "cumple_politica":  "Meets policy",
        "no_cumple":        "Does not meet policy",
        "si_cumple":        "Meets configured policy",

        # Crack time
        "tiempo_crackeo":        "Estimated crack time",
        "online_throttling":     "Online attack (throttled)",
        "online_no_throttling":  "Online attack (no throttle)",
        "offline_slow_hash":     "Offline — slow hash",
        "offline_fast_hash":     "Offline — fast hash",

        # Recommendations
        "recomendaciones": "Recommendations",
        "sin_hallazgos":   "No critical findings.",

        # Tab CSV Batch
        "lote_titulo":      "CSV Batch Evaluation",
        "lote_descripcion": (
            "Load a CSV file with passwords to evaluate them in bulk.\n"
            "Expected format:  username,password"
        ),
        "btn_cargar_csv":   "Load CSV file",
        "btn_exportar_lote": "Export results",
        "procesando":       "Processing...",
        "lote_completo":    "Batch done: {total} passwords evaluated.",
        "csv_error_formato": "The CSV file does not have the expected format.",
        "csv_col_usuario":  "Username",
        "csv_col_contrasena": "Password (hash)",
        "csv_col_puntaje":  "Score",
        "csv_col_categoria": "Category",
        "csv_col_entropia": "Entropy (bits)",
        "csv_col_filtrada": "In breaches",
        "csv_col_politica": "Meets policy",

        # Tab History
        "historial_titulo": "Evaluation History",
        "historial_vacio":  "No evaluations recorded yet.",
        "btn_borrar_todo":  "Clear history",
        "btn_borrar_sel":   "Delete selected",
        "confirmar_borrar": "Confirm deletion?",
        "confirmar_borrar_todo": "Delete all history? This action cannot be undone.",
        "hist_col_id":      "ID",
        "hist_col_fecha":   "Date",
        "hist_col_longitud": "Len.",
        "hist_col_puntaje": "Score",
        "hist_col_categoria": "Category",
        "hist_col_entropia": "Entropy",
        "hist_col_filtrada": "Breached",
        "hist_col_politica": "Policy",
        "total_registros":  "Total: {n} records",

        # Tab Settings
        "config_titulo":       "Policy Settings",
        "config_longitud":     "Minimum length (characters)",
        "config_mayusculas":   "Require uppercase",
        "config_minusculas":   "Require lowercase",
        "config_digitos":      "Require digits",
        "config_simbolos":     "Require symbols",
        "config_entropia":     "Minimum entropy (bits)",
        "config_score":        "Minimum acceptable score (0–4)",
        "config_idioma":       "Interface language",
        "btn_guardar_config":  "Save settings",
        "btn_restaurar":       "Restore defaults",
        "config_guardada":     "Settings saved successfully.",
        "config_restaurada":   "Settings restored to defaults.",

        # PDF
        "pdf_titulo":          "Password Evaluation Report",
        "pdf_fecha":           "Date",
        "pdf_resumen":         "Summary",
        "pdf_contrasena":      "Evaluated password",
        "pdf_longitud":        "Length",
        "pdf_mascara":         "(length: {n} characters)",
        "pdf_hallazgos":       "Findings",
        "pdf_recomendaciones": "Recommendations",
        "pdf_generado":        "PDF report generated: {ruta}",
        "pdf_error":           "Error generating PDF: {error}",

        # General errors
        "error_titulo":        "Error",
        "error_conexion":      "No internet connection.",
        "error_archivo":       "Could not open the file.",
        "error_generico":      "An unexpected error occurred.",
        "advertencia":         "Warning",
        "informacion":         "Information",

        # Recommendations (generated by core/recommendations.py)
        "rec_en_filtraciones":   "CRITICAL: This password has appeared {n} times in public data breaches. Change it immediately and never reuse it elsewhere.",
        "rec_no_diccionario":    "Avoid dictionary words or predictable patterns. Attackers test these exhaustively in the early phases of an attack.",
        "rec_score_bajo":        "The security score is very low. Consider using a passphrase: 4 or 5 random words chained together are both stronger and easier to remember.",
        "rec_aumentar_longitud": "Increase the length to at least {n} characters. Each additional character multiplies the crack time exponentially.",
        "rec_agregar_mayusculas":"Include at least one uppercase letter (A–Z) to expand the character space.",
        "rec_agregar_minusculas":"Include lowercase letters (a–z).",
        "rec_agregar_digitos":   "Add at least one digit (0–9).",
        "rec_agregar_simbolos":  "Add special symbols like @, #, $, !, % or ^ to significantly increase complexity.",
        "rec_baja_entropia":     "The calculated entropy ({entropia:.1f} bits) is too low. Use a broader mix of character types or a longer password.",
        "rec_leetspeak_simple":  "Simple leetspeak substitutions (a→@, e→3, o→0) are well-known and included in modern attack dictionaries. They add no real security.",
        "rec_sin_problemas":     "Excellent! No significant issues detected. Remember to use unique passwords for every service and enable two-factor authentication wherever possible.",
        "rec_usar_gestor":       "Use a password manager (Bitwarden, KeePass, 1Password) to generate and store long, unique, random passwords for each service.",
    },
}

_idioma_activo: str = "es"


def t(clave: str, **kwargs) -> str:
    """
    Devuelve el texto en el idioma activo.
    Admite sustitución de variables: t('lote_completo', total=42)
    """
    texto = IDIOMAS.get(_idioma_activo, IDIOMAS["es"]).get(clave, clave)
    if kwargs:
        try:
            texto = texto.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return texto


def cambiar_idioma(idioma: str) -> None:
    global _idioma_activo
    if idioma in IDIOMAS:
        _idioma_activo = idioma


def idioma_activo() -> str:
    return _idioma_activo


def idiomas_disponibles() -> list[str]:
    return list(IDIOMAS.keys())
