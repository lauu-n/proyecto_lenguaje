# Cocosette — DSL para Ciencia de Datos y Visualización

Proyecto de curso — **Lenguajes de Programación y Transducción**
Universidad Sergio Arboleda — Semestre 2026-2
Docente: Joaquín F. Sánchez

`Cocosette` es un lenguaje de dominio específico (DSL) temático que permite
describir, con una sintaxis declarativa y encadenada (`|>`), flujos
reproducibles de carga, preparación, análisis y visualización de datos,
sin escribir directamente el código Python subyacente. Todo el motor
subyacente se implementa desde cero en Python puro, sin librerías externas
de manipulación de datos o graficación (sin pandas, NumPy ni Matplotlib).

**Caso de estudio elegido: Ventas.** Se seleccionó el dataset de *ventas* por tener la menor complejidad léxica: requiere literales numéricos, cadenas y fechas como texto, sin unidades técnicas especializadas.

---

## Estado del proyecto y Alcance

Este repositorio implementa y valida la gramática y el front-end del lenguaje:

- **Tokens temáticos de Cocosette:** Prefijados internamente con convención `COCO*` (`COCOCARGAR`, `COCOFILTRAR`, `COCOGRAFICAR`, etc.).
- **Operaciones de Corte I:**
  - Asignaciones de variables.
  - Carga de datasets CSV (`cargar "datos/ventas.csv"`).
  - Selección de columnas (`seleccionar [col1, col2]`).
  - Filtros condicionales (`filtrar donde expresion`).
  - Declaración sintáctica de gráficos (`graficar barras ...`).
- **Operaciones extendidas de Corte II:**
  - Creación de columnas calculadas (`crear total = unidades * precio`).
  - Ordenamiento (`ordenar por columna [asc | desc]`).
  - Renombrado de columnas (`renombrar col_vieja como col_nueva`).
  - Limpieza de duplicados (`eliminar_duplicados`).
  - Tratamiento de nulos (`eliminar_nulos`, `rellenar_nulos col con expr`).
  - Conversión de tipos (`convertir col a entero | decimal | texto | booleano`).
  - Agrupamiento y agregaciones (`agrupar por [col] |> resumir ...`).
  - Exportación de resultados a CSV (`guardar resumen como "salidas/resumen.csv"`).
- **Validador de sintaxis:** Script `src/validar.py` con `ColectorDeErrores` basado en ANTLR4.

---

## Estructura del repositorio

```
proyecto_coco_actualizado/
├── README.md                  Documentación general del DSL
├── requirements.txt           Dependencias (antlr4-python3-runtime)
├── Makefile                   Automatización de compilación y validación
├── .gitignore                 Archivos ignorados (artefactos generados de ANTLR)
├── grammar/
│   └── Cocosette.g4           Gramática ANTLR4 (lexer + parser)
├── docs/
│   ├── documento_alcance.md   Especificación formal y alcance del lenguaje
│   └── conceptos_antlr.md     Guía de fundamentos de ANTLR4
├── datos/
│   └── ventas.csv             Dataset de prueba
├── ejemplos/
│   ├── validos/               Programas .coco válidos (Corte I y Corte II)
│   └── invalidos/             Programas .coco con errores sintácticos/léxicos
├── src/
│   ├── validar.py             Script que valida archivos .coco
│   └── parser/                Archivos generados automáticamente por ANTLR
└── salidas/                   Carpeta para guardar gráficos y CSVs exportados
```

---

## Requisitos y Puesta en Marcha

- Python 3.11 o superior
- Java (JDK 11+) y ANTLR 4.13.2
- Runtime de ANTLR4:
  ```bash
  pip install -r requirements.txt
  ```

### 1. Generar el lexer y el parser con ANTLR4

```bash
make generar
```
*(Equivale a ejecutar ANTLR4 sobre `grammar/Cocosette.g4` y exportar a `src/parser/`).*

### 2. Validar los programas de prueba

```bash
make validar
```

Ejecuta `src/validar.py` sobre todos los archivos `.coco` en `ejemplos/validos/` y `ejemplos/invalidos/`.

---

## Próximos pasos (Corte II y III)

- **Corte II:** Implementación del patrón Visitor, tabla de símbolos, evaluación semántica y ejecución de pipelines.
- **Corte III:** Renderizado autónomo de gráficos a imagen PNG, CLI interactiva y visualizaciones del caso de estudio.
