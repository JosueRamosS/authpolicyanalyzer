# Guía de Preparación: Defensa de Proyecto "AuthPolicyAnalyzer"

A continuación, encontrarás 20 preguntas técnicas de nivel avanzado (adecuadas para un estudiante de 5to año de Ingeniería de Software) que tu profesor podría hacerte, acompañadas de las respuestas sugeridas basadas en la arquitectura y código de tu proyecto.

---

## 1. Arquitectura y Diseño de Software

**P1: ¿Qué patrón arquitectónico utilizaste para estructurar la aplicación y por qué?**
**R:** Utilicé una arquitectura por capas (Layered Architecture). Separé el proyecto en módulos claros: `core` para la lógica de dominio pura (cálculo de entropía, zxcvbn), `data` para la persistencia (SQLite), `services` para integraciones externas (API de HIBP), `batch` para el procesamiento masivo y `ui` para la presentación. Esto garantiza un bajo acoplamiento, alta cohesión y facilita las pruebas unitarias al mantener la lógica de negocio independiente de la interfaz gráfica y de la base de datos.

**P2: ¿Cómo garantizas que la interfaz gráfica (PyQt5) no se congele cuando evalúas un archivo CSV de 10,000 registros?**
**R:** (Asumiendo la implementación típica con PyQt5, como se indica en `ui/widgets/thread_workers.py`): Desacoplé el procesamiento pesado del hilo principal de la interfaz utilizando hilos asíncronos (`QThread`). El `csv_processor` corre en un *Worker Thread* y se comunica con la UI a través de *Signals* y *Slots* para actualizar la barra de progreso de manera segura, sin bloquear el *Event Loop* principal.

**P3: ¿Por qué decidiste no usar un ORM (Object-Relational Mapping) como SQLAlchemy y optar por queries directas con sqlite3?**
**R:** Dado que el modelo de datos es bastante plano (esencialmente dos tablas: `evaluaciones` y `configuracion`) y el enfoque principal del software es el rendimiento, un ORM agregaba *overhead* innecesario y dependencias adicionales. Utilicé sentencias preparadas nativas de `sqlite3` y habilité el modo WAL (`PRAGMA journal_mode=WAL`) para asegurar un alto rendimiento de escritura y lecturas concurrentes sin bloqueo.

---

## 2. Seguridad y Privacidad

**P4: La rúbrica exige verificar contra bases de contraseñas comprometidas. ¿Cómo envías las contraseñas a la API sin exponer la privacidad del usuario?**
**R:** Implementé el protocolo *k-anonymity* utilizando la API de *Have I Been Pwned* (HIBP). El sistema calcula el hash SHA-1 de la contraseña localmente y envía **solamente los primeros 5 caracteres** (el prefijo) a la API a través de una conexión HTTPS. La API devuelve una lista de sufijos coincidentes y el conteo de filtraciones. La comprobación final de si nuestro hash completo está en esa lista se hace de manera local. La contraseña real jamás abandona el dispositivo.

**P5: En tu base de datos SQLite mantienes un historial. Si un atacante roba el archivo `authpolicyanalyzer.db`, ¿qué información obtiene?**
**R:** Ninguna contraseña en texto plano. En la tabla `evaluaciones` solo guardo el hash SHA-256 de las contraseñas, junto con los metadatos estadísticos (longitud, entropía, puntaje zxcvbn, recomendaciones y fecha). Extraer la contraseña original a partir del hash SHA-256 requeriría fuerza bruta local, pero el riesgo de filtración directa de la base de datos del sistema está mitigado.

**P6: ¿Cómo evitas ataques de inyección SQL (SQLi) al guardar el historial en SQLite?**
**R:** Utilizo *Parameter Binding* (consultas parametrizadas con el operador `?`) provisto por la librería `sqlite3` en todos mis métodos de `DatabaseManager`. Esto asegura que los datos insertados, como los hallazgos en formato JSON o los resultados, sean tratados estrictamente como literales y nunca concatenados dinámicamente como código SQL ejecutable.

**P7: Si un usuario corre el programa sin conexión a internet, ¿falla la aplicación al intentar contactar a Have I Been Pwned?**
**R:** No, el sistema tiene una degradación elegante (*graceful degradation*). En el módulo `services/hibp.py`, el bloque de solicitud captura excepciones de conexión (`RequestException`, `Timeout`). Si fallan, la función retorna `disponible=False` y el motor de análisis simplemente marca que la validación contra HIBP no pudo realizarse, pero continúa calculando la entropía, el ataque de diccionario local y el score de zxcvbn.

---

## 3. Algoritmos y Lógica de Evaluación

**P8: ¿De dónde sacas exactamente el valor matemático de la "Entropía"? ¿Cómo la estás calculando?**
**R:** La entropía teórica de Shannon (en bits) se calcula basándose en el espacio de caracteres disponible y la longitud de la clave. En `core/analyzer.py`, primero determino qué juego de caracteres usa la contraseña (minúsculas=26, mayúsculas=26, dígitos=10, símbolos=33) sumando las combinaciones. Luego aplico la fórmula: $Entropía = L \times \log_2(R)$, donde $L$ es la longitud de la contraseña y $R$ es el tamaño del espacio de caracteres.

**P9: Veo que usas zxcvbn. Si ya calculas la entropía teóricamente, ¿por qué dependes de la librería zxcvbn?**
**R:** La entropía teórica pura asume distribuciones de caracteres aleatorias, lo cual es falso para las contraseñas creadas por humanos. Una contraseña como "Abcdefghij1!" tiene alta entropía teórica pero es predecible. `zxcvbn` complementa esto calculando la entropía *real* mediante algoritmos de coincidencia de patrones espaciales (teclado QWERTY), diccionarios, fechas y nombres comunes, ofreciendo una estimación de fuerza bruta mucho más realista.

**P10: Mencionas simular ataques de diccionario. ¿Cómo funciona tu módulo de diccionario sin consumir toda la memoria RAM o CPU?**
**R:** En lugar de generar proactivamente millones de permutaciones (que tiene complejidad exponencial), utilizo un enfoque inverso (`core/dictionary_attack.py`). Tomo la contraseña ingresada y le aplico transformaciones de simplificación limitadas (pasar a minúsculas, remover el último número/símbolo, o invertir sustituciones *leetspeak* clásicas como "@" -> "a"). Las variaciones resultantes (que son muy pocas, máximo 10 o 15) se buscan en un `Set` en memoria cargado desde `common_passwords.txt`, ofreciendo complejidad de búsqueda $O(1)$.

**P11: ¿Qué es el "leetspeak" y cómo lo mitigaste en el simulador de diccionarios?**
**R:** El *leetspeak* es la práctica de sustituir letras por números o símbolos similares (ej. "p4ssw0rd"). En el módulo `dictionary_attack`, utilizo un mapeo inverso determinista (ej. si veo un '4' o un '@', pruebo sustituirlo por 'a') sobre el string para reducirlo a su forma de palabra original. Si la forma simplificada coincide con una palabra del diccionario de filtraciones locales, marco la contraseña como vulnerable.

**P12: ¿Cómo calculas el porcentaje de la barra visual de fortaleza en la UI?**
**R:** Combino el puntaje discreto de zxcvbn (0 a 4) con un bono de entropía continua. El puntaje base equivale al 25% por punto (ej. un score 3 es 75%). A esto le añado un margen adicional dinámico (hasta 10 puntos extra) si la contraseña posee una alta entropía teórica. El resultado final se limita al rango máximo de 100%.

---

## 4. Estructuras de Datos y Eficiencia

**P13: ¿Qué estructura de datos utilizas para validar contra el diccionario local (`common_passwords.txt`) y por qué?**
**R:** Uso un conjunto (`Set` de Python) que implementa una tabla hash por debajo (Hash Table). Esto me garantiza búsquedas de pertenencia (operación `in`) en tiempo $O(1)$ en promedio. Al arrancar la aplicación, leo el archivo e inserto las palabras en el set, cacheándolo en memoria.

**P14: En el procesamiento por lotes (CSV), ¿cómo manejas la caché de llamadas de red (HIBP) para no hacer "Rate Limiting"?**
**R:** Implementé un mecanismo de caché en memoria dentro del módulo `hibp.py`. Utilizo un diccionario (`Dict`) donde la clave es el prefijo de 5 caracteres SHA-1 y el valor es la respuesta en bruto de la API. Como en un lote institucional muchas contraseñas pueden compartir el mismo prefijo o ser idénticas, evito peticiones HTTP duplicadas, reduciendo enormemente la latencia y previniendo que la API me bloquee (Rate Limit).

**P15: ¿Cómo identifica el sistema las columnas en el CSV, dado que diferentes organizaciones podrían nombrarlas distinto?**
**R:** Utilizo detección heurística en `batch/csv_processor.py`. Normalizo la primera fila (minúsculas, quitando espacios) y verifico si los nombres intersectan con conjuntos de alias predefinidos (ej. `{"usuario", "user", "username"}` y `{"contrasena", "password", "clave"}`). Además, utilizo `csv.Sniffer` para detectar dinámicamente el delimitador (coma o punto y coma) independientemente de cómo se genere.

---

## 5. Mantenibilidad, Patrones y Código

**P16: En tu clase `ResultadoAnalisis`, veo que usas `@dataclass`. ¿Qué ventaja te proporciona esto frente a una clase tradicional de Python o un Diccionario?**
**R:** Usar `dataclass` proporciona tipado estático estricto (Type Hinting) fundamental para el autocompletado y análisis estático (mypy). Me ahorra el código repetitivo del `__init__`, `__repr__` y me ofrece un método sencillo (`asdict()`) para serializar el objeto directamente a JSON (para la exportación) o a SQL, todo manteniendo un código mucho más limpio y predecible que un diccionario crudo.

**P17: ¿Cómo inyectas y manejas la configuración o "Política de la empresa"?**
**R:** La configuración reside en la base de datos SQLite y se carga al inicio. Se inyecta en la lógica del negocio mediante un objeto `Criterios` (`core/criteria.py`). Durante el análisis, el pipeline evalúa `criterios.verificar(resultado)` para comparar métricas como entropía y longitud contra lo esperado. Esto facilita que una empresa exija 14 caracteres y 50 bits de entropía sin tener que modificar o recompilar el código fuente.

**P18: Veo que hay un archivo para `json_export`. ¿Qué consideraciones tuviste al serializar objetos complejos a JSON?**
**R:** La librería `zxcvbn` devuelve algunas propiedades en tipos específicos (como objetos `timedelta` para tiempos de crackeo) que el serializador JSON estándar no soporta y causaría un `TypeError`. Implementé una función recursiva de limpieza en `json_export.py` que atraviesa el diccionario y castea tipos desconocidos a `str`, eliminando cualquier riesgo de error al integrar nuestra salida con sistemas de auditoría externos.

**P19: ¿Cómo aseguras la internacionalización (i18n) de la interfaz y del PDF para que esté en inglés y en español?**
**R:** Extraje todas las cadenas literales a un módulo `ui/i18n.py`. En toda la aplicación (incluyendo la generación de PDFs), los textos se obtienen llamando a una función `t("clave")`, la cual busca la traducción correcta basada en el idioma configurado en la base de datos (y la política activa). Esto respeta el principio "Single Source of Truth" y facilita añadir un tercer idioma (ej. Portugués) mañana.

**P20: Si quisieras evolucionar el sistema hacia una arquitectura Cloud/Web, ¿qué parte de tu código requeriría cambios y cuál no?**
**R:** La arquitectura por capas brilla aquí. Todo el `core` (motor zxcvbn, entropía, simulador de diccionario) y `services` son reutilizables de forma directa (probablemente detrás de un framework web como FastAPI o Flask). La capa `data` podría migrarse fácilmente a PostgreSQL cambiando la cadena de conexión. Lo único descartado sería la carpeta `ui` (PyQt5), ya que sería reemplazada por una SPA web (React, Vue) que consumiría la nueva API, sin requerir reescribir la lógica de validación de seguridad.
