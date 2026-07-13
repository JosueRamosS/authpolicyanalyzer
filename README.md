# AuthPolicyAnalyzer

**Analizador de Fortaleza de Políticas de Autenticación**  
*Authentication Policy Strength Analyzer*

---

## Descripción / Description

**ES:** Aplicación de escritorio para evaluar la fortaleza de contraseñas, verificar
filtraciones públicas y configurar políticas de autenticación. Desarrollada como
proyecto académico de ciberseguridad con énfasis en privacidad: ninguna contraseña
se almacena en texto plano ni sale del sistema.

**EN:** Desktop application for evaluating password strength, checking public data
breaches, and configuring authentication policies. Built as an academic cybersecurity
project with a privacy-first design: no password is ever stored in plaintext or
transmitted beyond the local system.

---

## Requisitos del sistema / System Requirements

| Componente | Versión mínima |
|------------|---------------|
| Python     | 3.9+          |
| PyQt5      | 5.15.0+       |
| zxcvbn     | 4.4.28+       |
| requests   | 2.28.0+       |
| reportlab  | 4.0.0+        |

---

## Instalación / Installation

```bash
# 1. Clonar o descargar el proyecto / Clone or download the project
cd authpolicyanalyzer

# 2. Crear entorno virtual (recomendado) / Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows

# 3. Instalar dependencias / Install dependencies
pip install -r requirements.txt
```

---

## Ejecución / How to Run

```bash
python main.py
```

La base de datos SQLite (`authpolicy.db`) se crea automáticamente en la carpeta
del proyecto al primer inicio.

*The SQLite database (`authpolicy.db`) is created automatically in the project
folder on first launch.*

---

## Funcionalidades / Features

| # | ES | EN |
|---|----|----|
| 1 | Evaluación por longitud, complejidad y entropía real | Evaluation by length, complexity, and real entropy |
| 2 | Verificación de filtraciones (HIBP) con k-anonimato | Breach check (HIBP) with k-anonymity |
| 3 | Simulación de ataque de diccionario con variantes leetspeak | Dictionary attack simulation with leetspeak variants |
| 4 | Puntaje de fortaleza 0–4 con barra visual coloreada | Strength score 0–4 with colored visual bar |
| 5 | Recomendaciones automáticas en el idioma activo | Automatic recommendations in the active language |
| 6 | Reporte PDF con ReportLab | PDF report with ReportLab |
| 7 | Historial en SQLite (solo hash SHA-256, nunca texto plano) | SQLite history (SHA-256 hash only, never plaintext) |
| 8 | Evaluación en lote de archivos CSV | CSV batch evaluation |
| 9 | Criterios de política configurables y persistentes | Configurable and persistent policy criteria |
| 10 | Exportación JSON individual y de lote | Individual and batch JSON export |

---

## Formato del archivo CSV / CSV File Format

```csv
usuario,contrasena
alice,MiContrasena1!
bob,qwerty123
```

**ES:**
- Delimitadores aceptados: `,` `;` `|` `\t` (se detecta automáticamente)
- Codificación: UTF-8 o UTF-8 con BOM
- La primera fila puede ser cabecera (se detecta automáticamente)
- Columnas reconocidas para usuario: `usuario`, `user`, `username`, `nombre`, `name`
- Columnas reconocidas para contraseña: `contrasena`, `contraseña`, `password`, `pass`, `pwd`, `clave`
- Se ignoran columnas adicionales
- Máximo recomendado: 10 000 filas

**EN:**
- Accepted delimiters: `,` `;` `|` `\t` (auto-detected)
- Encoding: UTF-8 or UTF-8 with BOM
- Header row is auto-detected
- Recognized user columns: `usuario`, `user`, `username`, `nombre`, `name`
- Recognized password columns: `contrasena`, `contraseña`, `password`, `pass`, `pwd`, `clave`
- Extra columns are ignored
- Recommended maximum: 10,000 rows

Un archivo de ejemplo se incluye en `ejemplo_lote.csv`.  
*A sample file is included as `ejemplo_lote.csv`.*

---

## Arquitectura / Architecture

```
authpolicyanalyzer/
├── main.py                     # Punto de entrada / Entry point
├── requirements.txt
├── ejemplo_lote.csv            # CSV de muestra / Sample CSV
│
├── core/                       # Lógica de análisis / Analysis logic
│   ├── analyzer.py             #   Pipeline principal, ResultadoAnalisis
│   ├── criteria.py             #   Criterios configurables de política
│   ├── dictionary_attack.py    #   Simulador de ataque de diccionario
│   └── recommendations.py      #   Generador de recomendaciones
│
├── data/                       # Capa de datos / Data layer
│   ├── database.py             #   DatabaseManager (SQLite, WAL)
│   └── common_passwords.txt    #   Diccionario de contraseñas comunes
│
├── services/                   # Servicios externos / External services
│   └── hibp.py                 #   API Have I Been Pwned (k-anonimato)
│
├── reports/                    # Generación de reportes / Report generation
│   ├── pdf_report.py           #   Reporte PDF (ReportLab)
│   └── json_export.py          #   Exportación JSON
│
├── batch/                      # Procesamiento en lote / Batch processing
│   └── csv_processor.py        #   Procesador de archivos CSV
│
└── ui/                         # Interfaz gráfica / Graphical interface
    ├── main_window.py          #   VentanaPrincipal (PyQt5)
    ├── styles.py               #   Estilo neobrutalista (QSS)
    ├── i18n.py                 #   Internacionalización ES/EN
    └── widgets/
        ├── strength_bar.py     #   Barra de fortaleza animada
        └── thread_workers.py   #   Workers QThread (HIBP, CSV)
```

### Capas / Layers

| Capa | Descripción |
|------|-------------|
| `core` | Pura lógica de dominio, sin dependencias de UI ni BD |
| `data` | Acceso a SQLite, esquema, migraciones |
| `services` | Comunicación con APIs externas con degradación elegante |
| `reports` | Generación de artefactos (PDF, JSON) |
| `batch` | Orquestación del procesamiento en lote |
| `ui` | Presentación, sin lógica de negocio |

---

## Privacidad y Seguridad / Privacy & Security

- Las contraseñas evaluadas **nunca se almacenan en texto plano**. Solo se guarda
  el hash SHA-256 y los metadatos del análisis.
- Para la verificación HIBP, únicamente los **primeros 5 caracteres del hash SHA-1**
  (prefijo k-anónimo) se envían a la API. La contraseña completa y el hash completo
  **nunca salen del sistema**.
- La aplicación **no falla sin internet**: HIBP degrada elegantemente mostrando
  "no disponible".

---

*Passwords evaluated are **never stored in plaintext**. Only SHA-256 hash and
metadata are saved. For HIBP, only the **first 5 characters of the SHA-1 hash**
(k-anonymous prefix) are sent to the API. The application **does not crash without
internet**: HIBP degrades gracefully.*

---

## Licencia / License

Proyecto académico — uso educativo.  
*Academic project — educational use.*
