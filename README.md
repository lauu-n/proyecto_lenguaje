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
│   ├── corte2/                Demostraciones oficiales del Corte II
│   ├── validos/               Programas .coco validos generales
│   └── invalidos/             Programas .coco con errores lexicos, sintacticos y semanticos
├── src/
│   ├── main.py                Punto de entrada principal para ejecutar scripts .coco
│   ├── visitor.py             Interprete semantico Visitor (evaluacion y transformaciones)
│   ├── tabla.py               Motor tabular puro en Python (sin pandas/numpy)
│   ├── memoria_ejecucion.py   Memoria de variables y tabla de simbolos
│   ├── validar.py             Validador sintactico y lexico
│   └── parser/                Archivos generados automaticamente por ANTLR
└── salidas/                   Carpeta para guardar CSVs exportados y graficos
```

---

## Requisitos y Puesta en Marcha

- Python 3.10 o superior
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

### 2. Validar sintácticamente los archivos

```bash
python3 src/validar.py ejemplos/corte2/*.coco
```

### 3. Ejecutar los programas del DSL (Corte II)

```bash
# Demostración 1: Limpieza y tratamiento de nulos
python3 src/main.py ejemplos/corte2/01_limpieza_preprocesamiento.coco

# Demostración 2: Columnas calculadas y ordenamiento
python3 src/main.py ejemplos/corte2/02_transformacion_y_calculo.coco

# Demostración 3: Agrupación, estadísticas y exportación a CSV
python3 src/main.py ejemplos/corte2/03_agrupacion_y_estadisticas.coco
```

---

## Estado de Avance por Cortes

- [x] **Corte I (Completado):** Especificación del lenguaje, gramática ANTLR4, lexer, parser y validación sintáctica.
- [x] **Corte II (Completado):** Intérprete Visitor (`src/visitor.py`), memoria de variables (`src/memoria_ejecucion.py`), motor de datos inmutable en Python puro sin librerías externas (`src/tabla.py`), punto de entrada (`src/main.py`), 3 demostraciones funcionales y pruebas de errores semánticos.
- [ ] **Corte III:** Renderizado autónomo de gráficos a imagen PNG, CLI interactiva y visualizaciones avanzadas.
