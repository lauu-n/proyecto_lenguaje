# FlujoDatos — DSL para Ciencia de Datos y Visualización

Proyecto de curso — **Lenguajes de Programación y Transducción**
Universidad Sergio Arboleda — Semestre 2026-2
Docente: Joaquín F. Sánchez

`FlujoDatos` es un lenguaje de dominio específico (DSL) que permite
describir, con una sintaxis declarativa y encadenada (`|>`), flujos
reproducibles de carga, preparación, análisis y visualización de datos,
sin escribir directamente el código Python subyacente. Ese código
subyacente (Cortes 2 y 3) se implementa desde cero en Python puro: el
equipo decidió no depender de pandas, NumPy ni Matplotlib aunque el
enunciado del curso las sugiere como apoyo opcional — ver la
justificación en [`docs/documento_alcance.md`](docs/documento_alcance.md#2-usuarios-entradas-salidas-y-restricciones).

**Caso de estudio elegido: Ventas.** De las opciones sugeridas en el
enunciado (ventas, movilidad, datos ambientales, educación, salud
pública, telecomunicaciones), se seleccionó *ventas* por tener la
menor complejidad léxica: solo requiere literales numéricos, cadenas
y fechas como texto, sin unidades técnicas, códigos especializados ni
estructuras geoespaciales. La justificación completa está en
[`docs/documento_alcance.md`](docs/documento_alcance.md).

## Estado del proyecto: Corte 1 — Especificación y front-end

Esta entrega cubre únicamente el **front-end del lenguaje**:

- Definición del dominio, usuarios, entradas/salidas y restricciones.
- Palabras reservadas, operadores, literales y sentencias del Corte 1.
- Gramática formal en BNF/EBNF.
- Gramática implementada en ANTLR4 (`grammar/FlujoDatos.g4`).
- Programas de ejemplo correctos e incorrectos para validar el lexer
  y el parser (`ejemplos/`).

**No** incluye todavía ejecución semántica (Visitor), columnas
calculadas, agrupamientos/agregaciones, generación real de gráficas ni
exportación de archivos — eso corresponde a los Cortes 2 y 3. El
detalle de qué queda dentro y fuera de alcance está en el documento de
alcance.

## Estructura del repositorio

```
Proyecto_DSL_CienciaDatos/
├── README.md
├── requirements.txt
├── Makefile
├── .gitignore
├── grammar/
│   └── FlujoDatos.g4          Gramática ANTLR4 (lexer + parser)
├── docs/
│   ├── documento_alcance.md   Documento de instrucciones / alcance del DSL
│   └── conceptos_antlr.md     Guia de fundamentos de ANTLR (herencia, generacion de codigo)
├── datos/
│   └── ventas.csv             Dataset de ejemplo para el caso de estudio
├── ejemplos/
│   ├── validos/                3 programas .flujo sintácticamente correctos
│   └── invalidos/              3 programas .flujo con errores léxicos/sintácticos
├── src/
│   ├── validar.py              Script que valida .flujo con el parser generado
│   └── parser/                 Destino del código generado por ANTLR (ver abajo)
└── salidas/                    Carpeta destino de resultados (Cortes 2-3)
```

## Requisitos

- Python 3.11 o superior
- Java (JDK 11+) y ANTLR 4.13.2, para generar el lexer/parser
- Paquete `antlr4-python3-runtime` (ver `requirements.txt`)

## Puesta en marcha

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1. Generar el lexer y el parser en Python

El repositorio incluye la gramática (`.g4`) pero **no** el código que
ANTLR genera a partir de ella, porque es un artefacto reproducible.
Genéralo así:

```bash
make generar
# equivalente a:
# cd grammar && antlr4 -Dlanguage=Python3 -visitor -o ../src/parser FlujoDatos.g4
```

Esto crea `FlujoDatosLexer.py`, `FlujoDatosParser.py`,
`FlujoDatosVisitor.py` y los archivos `.tokens`/`.interp` dentro de
`src/parser/`. (Importante: hay que ejecutarlo desde dentro de
`grammar/`, o ANTLR replica la ruta relativa del `.g4` dentro de la
salida y termina creando `src/parser/grammar/...` en vez de dejar los
archivos directamente en `src/parser/`.)

¿Quieres entender exactamente qué genera cada clase y de dónde hereda?
Ver [`docs/conceptos_antlr.md`](docs/conceptos_antlr.md).

> Si tu entorno de calificación necesita el código ya generado dentro
> del repositorio, quita las líneas correspondientes de `.gitignore`
> y haz commit de esos archivos después de ejecutar `make generar`.

### 2. Validar los programas de ejemplo

```bash
make validar
```

Esto ejecuta `src/validar.py` sobre los tres programas válidos y los
tres inválidos, mostrando el árbol de análisis sintáctico o los
errores léxicos/sintácticos (con línea y columna) según corresponda.

## Próximos cortes

- **Corte 2:** patrón Visitor, tabla de símbolos, columnas calculadas,
  agrupamientos, agregaciones y estadísticas descriptivas.
- **Corte 3:** generación real de gráficas, exportación a PNG/CSV,
  interfaz de línea de comandos y caso de estudio completo.
