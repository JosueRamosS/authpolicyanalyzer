"""
reports/pdf_report.py
Generación de reportes PDF con ReportLab.
Diseño inspirado en la estética neobrutalista de la aplicación:
bordes sólidos, colores planos y tipografía en negrita.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.analyzer import ResultadoAnalisis

from reportlab.lib              import colors
from reportlab.lib.enums        import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes    import A4
from reportlab.lib.styles       import ParagraphStyle
from reportlab.lib.units        import cm
from reportlab.platypus         import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from ui import i18n

# ------------------------------------------------------------------
# Paleta neobrutalista
# ------------------------------------------------------------------
_NEGRO   = colors.HexColor("#1A1A1A")
_CREMA   = colors.HexColor("#FAF3E0")
_MORADO  = colors.HexColor("#7C3AED")
_GRIS_CL = colors.HexColor("#F9FAFB")
_GRIS_BD = colors.HexColor("#D1D5DB")

_COLOR_FORTALEZA = {
    "muy_debil":  colors.HexColor("#EF4444"),
    "debil":      colors.HexColor("#F97316"),
    "media":      colors.HexColor("#FACC15"),
    "fuerte":     colors.HexColor("#84CC16"),
    "muy_fuerte": colors.HexColor("#22C55E"),
}
_TEXTO_FORTALEZA = {
    "muy_debil": colors.white,
    "debil":     colors.white,
    "media":     _NEGRO,
    "fuerte":    _NEGRO,
    "muy_fuerte": _NEGRO,
}

# ------------------------------------------------------------------
# Estilos de párrafo
# ------------------------------------------------------------------

def _estilos() -> dict[str, ParagraphStyle]:
    blanco = {"textColor": colors.white, "backColor": _NEGRO}
    return {
        "titulo": ParagraphStyle(
            "titulo", fontName="Helvetica-Bold", fontSize=22,
            alignment=TA_CENTER, textColor=colors.white, spaceAfter=4,
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", fontName="Helvetica", fontSize=10,
            alignment=TA_CENTER, textColor=colors.HexColor("#9CA3AF"),
        ),
        "fecha_hdr": ParagraphStyle(
            "fecha_hdr", fontName="Helvetica", fontSize=8,
            alignment=TA_CENTER, textColor=colors.HexColor("#9CA3AF"), spaceBefore=2,
        ),
        "seccion": ParagraphStyle(
            "seccion", fontName="Helvetica-Bold", fontSize=11,
            textColor=colors.white, backColor=_NEGRO,
            leftIndent=8, rightIndent=0,
            spaceBefore=10, spaceAfter=4,
            borderPad=5,
        ),
        "normal": ParagraphStyle(
            "normal", fontName="Helvetica", fontSize=10, spaceBefore=2,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=10,
            leftIndent=16, spaceBefore=3, bulletIndent=6,
        ),
        "recom": ParagraphStyle(
            "recom", fontName="Helvetica", fontSize=9,
            leftIndent=20, spaceBefore=4, leading=13,
        ),
        "score_num": ParagraphStyle(
            "score_num", fontName="Helvetica-Bold", fontSize=28,
            alignment=TA_CENTER, textColor=colors.white,
        ),
        "score_label": ParagraphStyle(
            "score_label", fontName="Helvetica-Bold", fontSize=14,
            alignment=TA_CENTER,
        ),
        "score_entropia": ParagraphStyle(
            "score_entropia", fontName="Helvetica", fontSize=12,
            alignment=TA_CENTER, textColor=colors.white,
        ),
    }


# ------------------------------------------------------------------
# Función principal
# ------------------------------------------------------------------

def generar_pdf(resultado: ResultadoAnalisis, ruta: str) -> None:
    """
    Genera un PDF de evaluación en la ruta indicada.
    El idioma del reporte es el activo en ui.i18n en el momento de la llamada.
    La contraseña evaluada NO aparece en el PDF; solo su longitud (máscara).
    """
    directorio = os.path.dirname(ruta)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    doc = SimpleDocTemplate(
        ruta,
        pagesize=A4,
        leftMargin=2.4 * cm,
        rightMargin=2.4 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.5 * cm,
        title=i18n.t("pdf_titulo"),
        author="AuthPolicyAnalyzer",
    )
    ancho = doc.width
    e = _estilos()
    t = i18n.t
    story = []

    # ------------------------------------------------------------------
    # 1. CABECERA NEGRA
    # ------------------------------------------------------------------
    ahora = datetime.now().strftime("%Y-%m-%d  %H:%M")
    cab_datos = [
        [Paragraph("AuthPolicyAnalyzer", e["titulo"])],
        [Paragraph(t("app_subtitulo"),   e["subtitulo"])],
        [Paragraph(f"{t('pdf_fecha')}: {ahora}", e["fecha_hdr"])],
    ]
    cab = Table(cab_datos, colWidths=[ancho])
    cab.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), _NEGRO),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("LINEBELOW",    (0, -1), (-1, -1), 4, _MORADO),
    ]))
    story.append(cab)
    story.append(Spacer(1, 0.5 * cm))

    # ------------------------------------------------------------------
    # 2. BADGE DE FORTALEZA
    # ------------------------------------------------------------------
    col_fondo  = _COLOR_FORTALEZA.get(resultado.categoria, colors.gray)
    col_texto  = _TEXTO_FORTALEZA.get(resultado.categoria, colors.white)
    cat_texto  = t(resultado.clave_i18n)

    score_style = ParagraphStyle("sn", fontName="Helvetica-Bold", fontSize=30,
                                  alignment=TA_CENTER, textColor=col_texto)
    cat_style   = ParagraphStyle("sc", fontName="Helvetica-Bold", fontSize=16,
                                  alignment=TA_CENTER, textColor=col_texto, spaceBefore=2)
    ent_style   = ParagraphStyle("se", fontName="Helvetica", fontSize=11,
                                  alignment=TA_CENTER, textColor=col_texto)

    badge_datos = [[
        Paragraph(f"{resultado.puntaje}/4",         score_style),
        Paragraph(cat_texto,                         cat_style),
        Paragraph(
            f"{t('entropia')}<br/>"
            f"<b>{resultado.entropia:.1f}</b> {t('bits')}",
            ent_style,
        ),
    ]]
    badge = Table(badge_datos, colWidths=[ancho / 3] * 3)
    badge.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), col_fondo),
        ("BOX",           (0, 0), (-1, -1), 3,  _NEGRO),
        ("LINEAFTER",     (0, 0), (1, -1),  1,  _NEGRO),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(badge)
    story.append(Spacer(1, 0.45 * cm))

    # ------------------------------------------------------------------
    # 3. TABLA DE DETALLES
    # ------------------------------------------------------------------
    _si_no = lambda b: "Si" if b else "No"

    # Resultado HIBP
    if resultado.en_filtraciones:
        hibp_val = f"{resultado.veces_filtrada:,} {t('veces_filtrada')}"
    elif resultado.hibp_disponible:
        hibp_val = t("no_filtrada")
    else:
        hibp_val = t("hibp_error")

    # Resultado diccionario
    if resultado.en_diccionario:
        dic_val = f"{t('encontrada_dic')}: '{resultado.variante_diccionario}' ({resultado.esfuerzo_diccionario})"
    else:
        dic_val = t("no_encontrada_dic")

    detalles = [
        [t("pdf_contrasena"),  t("pdf_mascara", n=resultado.longitud)],
        [t("longitud"),        f"{resultado.longitud} {t('caracteres')}"],
        [t("puntaje"),         f"{resultado.puntaje}/4 — {cat_texto}"],
        [t("entropia"),        f"{resultado.entropia:.2f} {t('bits')}"],
        ["Mayúsculas",         _si_no(resultado.tiene_mayusculas)],
        ["Minúsculas",         _si_no(resultado.tiene_minusculas)],
        ["Dígitos",            _si_no(resultado.tiene_digitos)],
        ["Símbolos",           _si_no(resultado.tiene_simbolos)],
        [t("filtraciones"),    hibp_val],
        [t("diccionario"),     dic_val],
        [t("cumple_politica"), _si_no(resultado.cumple_politica)],
    ]

    etiq_style = ParagraphStyle("et", fontName="Helvetica-Bold", fontSize=10,
                                 textColor=colors.white)
    val_style  = ParagraphStyle("vl", fontName="Helvetica", fontSize=10)

    det_data = [
        [Paragraph(k, etiq_style), Paragraph(str(v), val_style)]
        for k, v in detalles
    ]
    story.append(Paragraph(f"  {t('pdf_resumen').upper()}", e["seccion"]))
    story.append(Spacer(1, 0.15 * cm))

    det_table = Table(det_data, colWidths=[ancho * 0.34, ancho * 0.66])
    det_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), _NEGRO),
        ("GRID",          (0, 0), (-1, -1), 1,  _NEGRO),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(1, 0), (1, -1),
         [colors.white, _GRIS_CL] * (len(det_data) // 2 + 1)),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        # Bordes de sombra offset (neobrutalismo)
        ("LINEBELOW",     (0, -1), (-1, -1), 4, _NEGRO),
        ("LINEAFTER",     (-1, 0), (-1, -1), 4, _NEGRO),
    ]))
    story.append(det_table)

    # Incumplimientos de política (si los hay)
    if resultado.incumplimientos:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(f"  INCUMPLIMIENTOS DE POLÍTICA", e["seccion"]))
        story.append(Spacer(1, 0.15 * cm))
        for inc in resultado.incumplimientos:
            story.append(Paragraph(f"• {inc}", e["bullet"]))

    # ------------------------------------------------------------------
    # 4. HALLAZGOS
    # ------------------------------------------------------------------
    if resultado.hallazgos:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(f"  {t('pdf_hallazgos').upper()}", e["seccion"]))
        story.append(Spacer(1, 0.15 * cm))
        for h in resultado.hallazgos:
            story.append(Paragraph(f"• {h}", e["bullet"]))

    # ------------------------------------------------------------------
    # 5. RECOMENDACIONES
    # ------------------------------------------------------------------
    if resultado.recomendaciones:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(f"  {t('pdf_recomendaciones').upper()}", e["seccion"]))
        story.append(Spacer(1, 0.15 * cm))
        for idx, rec in enumerate(resultado.recomendaciones, 1):
            story.append(Paragraph(f"<b>{idx}.</b>  {rec}", e["recom"]))
            story.append(Spacer(1, 0.05 * cm))

    # ------------------------------------------------------------------
    # 6. PIE DE PÁGINA (canvas callback)
    # ------------------------------------------------------------------
    def _pie(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(_NEGRO)
        canvas.rect(0, 0, A4[0], 1.1 * cm, fill=True, stroke=False)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#9CA3AF"))
        canvas.drawString(
            2.4 * cm, 0.4 * cm,
            "AuthPolicyAnalyzer v1.0.0 — Proyecto Académico de Ciberseguridad",
        )
        canvas.drawRightString(
            A4[0] - 2.4 * cm, 0.4 * cm,
            datetime.now().strftime("%Y-%m-%d"),
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=_pie, onLaterPages=_pie)
