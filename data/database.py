"""
data/database.py
Gestor de base de datos SQLite para AuthPolicyAnalyzer.
Las contraseñas evaluadas NUNCA se almacenan en texto plano;
solo se guarda su hash SHA-256 junto con metadatos.
"""
from __future__ import annotations

import sqlite3
import os
import json
from datetime import datetime

DIRECTORIO_DATA = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(DIRECTORIO_DATA, "authpolicyanalyzer.db")

CONFIGURACION_PREDETERMINADA: dict[str, str] = {
    "longitud_minima":    "12",
    "requiere_mayusculas": "true",
    "requiere_minusculas": "true",
    "requiere_digitos":    "true",
    "requiere_simbolos":   "true",
    "entropia_minima":     "40.0",
    "score_minimo":        "3",
    "idioma":              "es",
}

DDL = """
CREATE TABLE IF NOT EXISTS evaluaciones (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha                TEXT    NOT NULL,
    hash_sha256          TEXT    NOT NULL,
    longitud             INTEGER NOT NULL DEFAULT 0,
    puntaje              INTEGER NOT NULL,
    categoria            TEXT    NOT NULL,
    entropia             REAL    DEFAULT 0.0,
    en_filtraciones      INTEGER DEFAULT 0,
    veces_filtrada       INTEGER DEFAULT 0,
    cumple_politica      INTEGER DEFAULT 0,
    hallazgos_json       TEXT    DEFAULT '[]',
    recomendaciones_json TEXT    DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS configuracion (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
"""


class DatabaseManager:
    """
    Capa de acceso a datos. Cada método abre y cierra su propia
    conexión para evitar problemas con hilos de la interfaz.
    """

    def __init__(self, ruta_db: str = RUTA_DB):
        self.ruta_db = ruta_db

    # ------------------------------------------------------------------
    # Conexión
    # ------------------------------------------------------------------

    def _conectar(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.ruta_db)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------

    def inicializar(self) -> None:
        """Crea las tablas e inserta la configuración predeterminada si no existe."""
        with self._conectar() as conn:
            conn.executescript(DDL)
            conn.executemany(
                "INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)",
                list(CONFIGURACION_PREDETERMINADA.items()),
            )

    # ------------------------------------------------------------------
    # Evaluaciones
    # ------------------------------------------------------------------

    def guardar_evaluacion(self, datos: dict) -> int:
        """
        Persiste una evaluación. El campo 'hash_sha256' es obligatorio.
        Devuelve el id generado.
        """
        with self._conectar() as conn:
            cursor = conn.execute(
                """
                INSERT INTO evaluaciones
                    (fecha, hash_sha256, longitud, puntaje, categoria,
                     entropia, en_filtraciones, veces_filtrada,
                     cumple_politica, hallazgos_json, recomendaciones_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datos.get("fecha", datetime.now().isoformat()),
                    datos["hash_sha256"],
                    datos.get("longitud", 0),
                    datos["puntaje"],
                    datos["categoria"],
                    datos.get("entropia", 0.0),
                    int(bool(datos.get("en_filtraciones", False))),
                    datos.get("veces_filtrada", 0),
                    int(bool(datos.get("cumple_politica", False))),
                    json.dumps(datos.get("hallazgos", []),        ensure_ascii=False),
                    json.dumps(datos.get("recomendaciones", []),  ensure_ascii=False),
                ),
            )
            return cursor.lastrowid  # type: ignore[return-value]

    def obtener_historial(self, limite: int = 500) -> list[dict]:
        """Devuelve evaluaciones ordenadas de más reciente a más antigua."""
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT * FROM evaluaciones ORDER BY id DESC LIMIT ?", (limite,)
            )
            filas = cursor.fetchall()
        resultado = []
        for fila in filas:
            d = dict(fila)
            d["hallazgos"]       = json.loads(d.get("hallazgos_json", "[]"))
            d["recomendaciones"] = json.loads(d.get("recomendaciones_json", "[]"))
            resultado.append(d)
        return resultado

    def obtener_evaluacion_por_id(self, id_evaluacion: int) -> dict | None:
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT * FROM evaluaciones WHERE id = ?", (id_evaluacion,)
            )
            fila = cursor.fetchone()
        if fila is None:
            return None
        d = dict(fila)
        d["hallazgos"]       = json.loads(d.get("hallazgos_json", "[]"))
        d["recomendaciones"] = json.loads(d.get("recomendaciones_json", "[]"))
        return d

    def borrar_evaluacion(self, id_evaluacion: int) -> None:
        with self._conectar() as conn:
            conn.execute("DELETE FROM evaluaciones WHERE id = ?", (id_evaluacion,))

    def borrar_historial(self) -> None:
        with self._conectar() as conn:
            conn.execute("DELETE FROM evaluaciones")

    def contar_evaluaciones(self) -> int:
        with self._conectar() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM evaluaciones")
            return cursor.fetchone()[0]

    # ------------------------------------------------------------------
    # Configuración
    # ------------------------------------------------------------------

    def obtener_configuracion(self) -> dict[str, str]:
        with self._conectar() as conn:
            cursor = conn.execute("SELECT clave, valor FROM configuracion")
            return {fila["clave"]: fila["valor"] for fila in cursor.fetchall()}

    def guardar_configuracion(self, clave: str, valor) -> None:
        with self._conectar() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)",
                (clave, str(valor)),
            )

    def guardar_configuracion_multiple(self, config: dict) -> None:
        with self._conectar() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)",
                [(k, str(v)) for k, v in config.items()],
            )

    def restaurar_predeterminada(self) -> None:
        with self._conectar() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)",
                list(CONFIGURACION_PREDETERMINADA.items()),
            )
