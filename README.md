# FlujoDatos — DSL para Ciencia de Datos y Visualización

Proyecto de **Lenguajes de Programación y Transducción**, Universidad
Sergio Arboleda, semestre 2026-2. Docente: Joaquín F. Sánchez.

## Estado: corte 1, especificación y front-end

FlujoDatos describe flujos declarativos mediante pipelines (`|>`). Esta
entrega reconoce asignaciones y expresiones, carga de CSV, selección,
filtros y una instrucción de visualización. Genera un árbol de análisis y
reporta errores léxicos y sintácticos. **No ejecuta operaciones de datos ni
produce gráficas:** semántica/Visitor corresponden al corte 2 y gráficas
al corte 3.

El caso de estudio es ventas: hay un CSV pequeño incluido que permite
describir cargas, selecciones y filtros. El equipo mantiene la decisión
de implementar el motor futuro en Python puro. No es una prohibición del
enunciado: pandas, NumPy y Matplotlib se presentan como apoyo opcional.

La especificación completa y el catálogo están en
[docs/documento_alcance.md](docs/documento_alcance.md).

## Ejecutar sin Git, Java ni Make

Se requiere Python 3.11 o superior. Descarga esta rama con **Code → Download
ZIP**, extrae el archivo y abre una consola en la carpeta que contiene este
README. Los archivos generados por ANTLR 4.13.2 ya están incluidos.

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe src/validar.py --arbol-completo "ejemplos/validos/*.flujo"
```

Si no tienes el lanzador `py`, usa `python` en el primer comando. No es
necesario activar el entorno ni cambiar políticas de ejecución.

### Linux/macOS (Bash)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/validar.py --arbol-completo 'ejemplos/validos/*.flujo'
```

También se puede ejecutar como módulo: `python -m src.validar archivo.flujo`.
En los comandos siguientes, `python` representa el ejecutable de tu entorno.

## Validación y pruebas

```text
python src/validar.py ejemplos/validos/01_carga_y_pipeline.flujo
python src/validar.py --arbol-completo "ejemplos/validos/*.flujo"
python src/validar.py "ejemplos/invalidos/*.flujo"
python -m unittest discover -s tests -v
```

La validación de los negativos debe mostrar errores y terminar con estado
1. **La suite**, en cambio, termina en 0 cuando todos los positivos se
aceptan y todos los negativos se rechazan según lo esperado. No confundir
«programa inválido detectado» con «prueba fallida».

| Estado de la consola | Significado |
|---|---|
| 0 | Todas las fuentes son léxica y sintácticamente válidas. |
| 1 | Al menos una fuente tiene errores o no pudo leerse. |
| 2 | Uso incorrecto de argumentos o dependencia/analizador ausente. |

Los diagnósticos se escriben en stderr, identifican su etapa y muestran
línea y columna desde 1. Los errores de lectura no cancelan el lote.
Las fuentes se leen en UTF-8, con BOM opcional. Los patrones de archivos
también se expanden dentro del programa para funcionar en PowerShell.

El árbol completo está disponible con `--arbol-completo`; sin esa opción
se muestra un resumen. Aceptar una variable no declarada es normal en
este corte, que todavía no comprueba semántica.

[Reporte de pruebas y límites de validación](docs/reporte_pruebas.md).

## Regeneración (solo al modificar la gramática)

La gramática activa es `grammar/FlujoDatos.g4`. `DSL.g4` en la raíz se
conserva únicamente como prototipo histórico; no se usa para esta entrega.
Los archivos de `src/parser/` se versionan porque el corte 1 exige código
generado, pero no deben editarse a mano.

1. Instala Java 11 o superior para desarrollo (por ejemplo, un JDK de
   [Eclipse Temurin](https://adoptium.net/temurin/releases/)).
2. Descarga el [JAR oficial de ANTLR 4.13.2](https://www.antlr.org/download/antlr-4.13.2-complete.jar)
   y guárdalo como `tools/antlr-4.13.2-complete.jar`.
3. Comprueba Java y regenera:

```text
java -version
python tools/generar.py
python -m unittest discover -s tests -v
```

Puedes indicar otras rutas:

```text
python tools/generar.py --antlr-jar "ruta/antlr-4.13.2-complete.jar" --java "ruta/java"
```

El script fija el directorio de trabajo para no generar una subcarpeta
accidental. El comando equivalente, ejecutado dentro de `grammar/`, es:

```text
java -jar ../tools/antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor -o ../src/parser FlujoDatos.g4
```

El generador y el runtime deben ser **4.13.2**. Se generan lexer, parser,
Visitor, Listener y archivos `.tokens`/`.interp`. El JAR descargado y los
entornos locales se excluyen de Git.

Para quien ya disponga de GNU Make, `make validar` ejecuta la suite y
`make generar` regenera. Usa `make validar PYTHON=python` si el ejecutable
se llama `python`; Make es opcional.

## Estructura

```text
grammar/FlujoDatos.g4       Gramática activa
DSL.g4                     Prototipo histórico, fuera del flujo de generación
src/validar.py             Análisis, diagnósticos y consola del corte 1
src/parser/                Artefactos generados con ANTLR 4.13.2
tests/test_frontend.py     Pruebas de reconocimiento, árboles, tokens y consola
tools/generar.py           Regeneración portable
docs/documento_alcance.md  Dominio, catálogo, EBNF y decisiones
docs/conceptos_antlr.md    Fundamentos y relación entre componentes
docs/reporte_pruebas.md    Evidencia de validación
datos/ventas.csv           Datos de ejemplo incluidos
datos/README.md            Esquema y límites de la información del dataset
ejemplos/validos/          Tres fuentes válidas
ejemplos/invalidos/        Tres fuentes inválidas
salidas/                  Destino futuro de resultados
```

## Próximos cortes

- **Corte 2:** Visitor, tabla de símbolos, lectura real de CSV,
  transformaciones, agregaciones, estadísticas, faltantes, validaciones
  semánticas y exportación a CSV.
- **Corte 3:** gráficas reales, exportación a PNG, interfaz de ejecución
  completa y caso de estudio integrado.
