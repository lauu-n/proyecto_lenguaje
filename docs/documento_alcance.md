# Documento de alcance — DSL `FlujoDatos`

**Curso:** Lenguajes de Programación y Transducción
**Proyecto:** Lenguaje de Dominio Específico para Ciencia de Datos y Visualización
**Corte:** 1 — Especificación y front-end del lenguaje
**Caso de estudio:** Ventas

---

## 1. Descripción general y dominio seleccionado

`FlujoDatos` es un DSL declarativo, basado en encadenamiento de
operaciones (`|>`), para describir flujos reproducibles de carga,
preparación, análisis y visualización de datos.

Se eligió **ventas** porque el repositorio ya dispone de un CSV de
ejemplo con cinco columnas, un esquema pequeño y operaciones fáciles de
demostrar. La elección mantiene continuidad con el vocabulario del curso.
No implica que otros dominios necesiten más tokens: sus unidades, códigos
o coordenadas también podrían representarse como cadenas y números.

Casos de uso del corte 1 (solo reconocimiento):

1. Describir la carga de `datos/ventas.csv` y asociarla a `ventas`.
2. Seleccionar `ciudad`, `unidades` y `precio`, y filtrar registros con
   unidades y precios positivos.
3. Describir una gráfica de barras por ciudad y una dispersión entre
   unidades y precio, sin producir aún imágenes.

## 2. Usuarios, entradas, salidas y restricciones

- **Usuarios:** estudiantes o analistas que quieran describir un flujo
  de análisis de datos de ventas sin escribir directamente el código
  Python que hace la carga, el filtrado, las agregaciones y las
  gráficas (código que, en este proyecto, se implementa desde cero,
  sin pandas/NumPy/Matplotlib — ver restricciones más abajo).
- **Entradas:** archivos fuente `.flujo` (programas del DSL) y, a
  partir del Corte 2, archivos CSV de datos reales.
- **Salidas:**
  - En este Corte 1: árbol de análisis sintáctico y reporte de errores
    léxicos/sintácticos con línea y columna.
  - En cortes futuros (fuera de alcance aquí): tablas transformadas,
    estadísticas, archivos CSV exportados e imágenes PNG de gráficas.
- **Restricciones de diseño** (justificadas en la sección 11):
  - Los identificadores solo admiten letras ASCII, dígitos y guion
    bajo (sin tildes ni "ñ"); se recomienda escribir `anio` en vez de
    `año`.
  - `x` y `y` son palabras reservadas (usadas en `graficar`) y no
    pueden usarse como nombre de columna o variable.
  - Las cadenas de texto no admiten saltos de línea internos.
  - Cada sentencia termina explícitamente en `;`.
  - **Sin bibliotecas de terceros para datos ni graficación.** El
    enunciado del curso sugiere pandas, NumPy y Matplotlib como apoyo
    opcional (ver requisitos técnicos del enunciado). Este equipo
    decide no usarlas: el motor de ejecución de los Cortes 2 y 3
    (lectura/escritura de CSV, filtrado, agregaciones, estadísticas
    descriptivas y generación de gráficas) se implementa con código
    propio sobre Python puro. Sí se permiten módulos de la librería
    estándar de Python (por ejemplo `csv`, `math`, `statistics`),
    porque son parte del lenguaje, no bibliotecas de ciencia de datos
    ya construidas para este dominio. `antlr4-python3-runtime` queda
    fuera de esta restricción porque el uso de ANTLR4 es un requisito
    técnico obligatorio del enunciado (sección 7), no una biblioteca
    opcional de apoyo.

## 3. Alcance de esta entrega (Corte 1)

**Incluido:**

- Delimitación del dominio y casos de uso (ventas).
- Diseño de palabras reservadas, operadores, literales y sentencias.
- Gramática formal en BNF/EBNF (sección 7).
- Gramática implementada en ANTLR4 (`grammar/FlujoDatos.g4`).
- Lexer, parser y Visitor/Listener base generados en Python con ANTLR
  4.13.2, incluidos en `src/parser/`, e instrucciones de regeneración.
- Reconocimiento sintáctico de: asignaciones, expresiones
  aritmético-lógicas, carga de CSV, selección de columnas, filtros con
  comparaciones simples y una instrucción de visualización.
- Programas de ejemplo correctos e incorrectos (`ejemplos/`) que
  validan el lexer y el parser.

**Fuera de alcance (planeado para cortes siguientes):**

- Corte 2: patrón Visitor, tabla de símbolos, columnas calculadas,
  agrupamiento, agregaciones, tratamiento de valores faltantes,
  escritura de resultados en CSV.
- Corte 3: generación real de las gráficas y exportación a PNG,
  interfaz de línea de comandos completa, caso de estudio final con
  datos reales.

En particular, aunque la gramática ya reconoce la sintaxis completa de
`graficar` (incluyendo los cinco tipos de gráfica), **no se produce
ninguna gráfica en este corte**: solo se valida que la instrucción esté
bien escrita.

## 4. Palabras reservadas

| Palabra | Uso |
|---|---|
| `cargar` | Cargar un archivo CSV |
| `seleccionar` | Seleccionar columnas dentro de un pipeline |
| `filtrar` | Filtrar filas dentro de un pipeline |
| `donde` | Introduce la condición de un filtro |
| `graficar` | Inicia una instrucción de visualización |
| `titulo` | Título opcional de una gráfica |
| `guardar` | Introduce la ruta de exportación de una gráfica |
| `como` | Acompaña a `guardar` |
| `barras`, `lineas`, `histograma`, `dispersion`, `caja` | Tipos de gráfica |
| `x`, `y` | Ejes de una gráfica |
| `verdadero`, `falso` | Literales booleanos |

Son 17 palabras reservadas en total: un vocabulario deliberadamente
pequeño para mantener baja la complejidad léxica del reconocedor.

## 5. Operadores, literales y tipos de datos

**Operadores aritméticos:** `+` `-` `*` `/` `%` `^`
**Operadores relacionales:** `<` `<=` `>` `>=` `==` `!=`
**Operadores lógicos:** `&&` `||` `!`
**Otros símbolos:** `=` (asignación), `|>` (pipeline), `( )` (agrupación),
`[ ]` (lista de columnas), `,` `;`

**Literales y tipos:**

| Tipo | Ejemplo | Descripción |
|---|---|---|
| Entero (`INT`) | `120` | Secuencia de dígitos |
| Decimal (`FLOAT`) | `0.15` | Dígitos, punto, dígitos |
| Cadena (`STRING`) | `"datos/ventas.csv"` | Entre comillas dobles, sin salto de línea |
| Booleano (`BOOLEANO`) | `verdadero`, `falso` | Palabras reservadas |

Los identificadores (`ID`) representan nombres de variables o de
columnas: deben iniciar con una letra o guion bajo, seguidos de
letras, dígitos o guion bajo.

## 6. Sentencias soportadas en el Corte 1

```
# Asignación simple con expresión
descuento = 0.15;

# Carga de un archivo CSV
ventas = cargar "datos/ventas.csv";

# Pipeline de selección y filtrado
ventas_filtradas = ventas
    |> seleccionar [fecha, ciudad, categoria, unidades, precio]
    |> filtrar donde unidades > 0 && precio > 0;

# Reconocimiento sintáctico de una visualización (no se genera aún)
graficar barras resumen
    x ciudad
    y precio
    titulo "Precio por ciudad"
    guardar como "salidas/precio_ciudad.png";
```

Restricciones de composición:

- Cada pipeline comienza con una variable ya escrita como identificador;
  la carga y el pipeline se expresan en dos sentencias distintas.
- `titulo` y `guardar como` son opcionales e independientes, pero, si se
  usan juntos, `titulo` aparece antes de `guardar como`.
- El lenguaje distingue mayúsculas: `cargar` es reservada y `Cargar` es ID.
- Los decimales exigen dígitos a ambos lados del punto: `0.5` es válido;
  `.5` y `1e3` no son formatos admitidos.

## 7. Gramática formal (BNF/EBNF)

La siguiente gramática EBNF describe el alcance del Corte 1. En la
implementación ANTLR4 (`grammar/FlujoDatos.g4`) la jerarquía de
expresiones se escribe de forma left-recursive, que ANTLR4 reescribe
internamente de forma equivalente a la mostrada aquí.

```ebnf
programa          ::= sentencia { sentencia } ;
sentencia         ::= asignacion ";" | sentenciaGraficar ";" ;

asignacion        ::= IDENTIFICADOR "=" fuenteDatos ;
fuenteDatos       ::= cargaCSV | pipeline | expresion ;
cargaCSV          ::= "cargar" CADENA ;
pipeline          ::= IDENTIFICADOR operacion { operacion } ;   (* al menos una *)
operacion         ::= "|>" ( seleccionOp | filtroOp ) ;
seleccionOp       ::= "seleccionar" "[" listaColumnas "]" ;
filtroOp          ::= "filtrar" "donde" expresion ;
listaColumnas     ::= IDENTIFICADOR { "," IDENTIFICADOR } ;

sentenciaGraficar ::= "graficar" tipoGrafica IDENTIFICADOR
                       "x" IDENTIFICADOR
                       "y" IDENTIFICADOR
                       [ "titulo" CADENA ]
                       [ "guardar" "como" CADENA ] ;
tipoGrafica       ::= "barras" | "lineas" | "histograma"
                     | "dispersion" | "caja" ;

expresion         ::= expOr ;
expOr             ::= expAnd { "||" expAnd } ;
expAnd            ::= expIgualdad { "&&" expIgualdad } ;
expIgualdad       ::= expRelacional { ( "==" | "!=" ) expRelacional } ;
expRelacional     ::= expAditiva { ( "<" | "<=" | ">" | ">=" ) expAditiva } ;
expAditiva        ::= expMultiplicativa { ( "+" | "-" ) expMultiplicativa } ;
expMultiplicativa ::= expPotencia { ( "*" | "/" | "%" ) expPotencia } ;
expPotencia       ::= expUnaria [ "^" expPotencia ] ;   (* asociativo a la derecha *)
expUnaria         ::= ( "-" | "!" ) expUnaria | expPrimaria ;
expPrimaria       ::= literal | IDENTIFICADOR | "(" expresion ")" ;

literal           ::= ENTERO | DECIMAL | CADENA | BOOLEANO ;
BOOLEANO          ::= "verdadero" | "falso" ;

IDENTIFICADOR     ::= LETRA { LETRA | DIGITO } ;
LETRA             ::= "a".."z" | "A".."Z" | "_" ;
DIGITO            ::= "0".."9" ;
ENTERO            ::= DIGITO { DIGITO } ;
DECIMAL           ::= DIGITO { DIGITO } "." DIGITO { DIGITO } ;
CADENA            ::= COMILLA { ESCAPE | CARACTER_CADENA } COMILLA ;
ESCAPE            ::= BARRA ( COMILLA | BARRA ) ;
COMILLA           ::= '"' ;
BARRA             ::= '\' ;
CARACTER_CADENA    ::= ? cualquier carácter Unicode excepto comilla, barra, CR y LF ? ;
COMENTARIO        ::= "#" { CARACTER_COMENTARIO } ;
CARACTER_COMENTARIO ::= ? cualquier carácter Unicode excepto CR y LF ? ;
ESPACIO           ::= ? espacio, tabulación, CR o LF ? ;
```

Se consume el archivo completo (equivalente a `EOF` en ANTLR); comentarios
y espacios se descartan entre tokens. Un programa vacío o compuesto solo
por comentarios no es válido. En las reglas léxicas se toma el token más
largo; a igual longitud, las palabras reservadas tienen prioridad sobre ID.

Solo se admiten `\"` (comilla) y `\\` (barra invertida) dentro de cadenas.
Una barra sin escape válido se rechaza; no se admiten `\n`, `\t` ni `\q`.
Para rutas de Windows se puede escribir `"C:/datos/ventas.csv"` o
`"C:\\datos\\ventas.csv"`. El corte 1 reconoce estos escapes; su
interpretación como valores corresponde al Visitor del corte 2.

## 8. Precedencia y asociatividad de operadores

De mayor a menor precedencia:

1. `- !` (unarios, prefijos)
2. `^` (potencia, asociativo a la derecha)
3. `* / %`
4. `+ -`
5. `< <= > >=`
6. `== !=`
7. `&&`
8. `||`

Los operadores binarios salvo `^` agrupan a la izquierda. Los unarios
agrupan desde el prefijo hacia su operando y tienen más prioridad que `^`.
Así, `-2 ^ 2` se reconoce como `(-2) ^ 2`, `2 ^ 3 ^ 2` como
`2 ^ (3 ^ 2)` y `2 ^ -3` como `2 ^ (-3)`. Se comprueba la estructura
del árbol sin calcular resultados numéricos.

## 9. Manejo de errores (Corte 1)

El front-end distingue dos niveles de error, ambos reportados con
línea y columna mediante un `ErrorListener` propio
(`src/validar.py`). Las coordenadas públicas empiezan en 1, se muestra
la categoría y un fragmento de la fuente con indicador de posición:

- **Léxico:** un carácter o secuencia no reconocida por ninguna regla
  del lexer (por ejemplo, una cadena sin comilla de cierre).
- **Sintáctico:** una secuencia de tokens válidos individualmente pero
  que no respeta ninguna producción de la gramática (por ejemplo, una
  sentencia sin `;`, o el uso de `x`/`y` como identificador).

El manejo semántico (variables no declaradas, columnas inexistentes,
tipos incompatibles) queda para el Corte 2, cuando exista una tabla de
símbolos.

Si una fuente no existe o no es UTF-8, se informa un error de entrada y
se continúa con los archivos restantes. El proceso termina con 0 si todos
son válidos, 1 si hay errores de fuente/lectura y 2 ante uso incorrecto
de la consola o dependencias ausentes. Los errores léxicos pueden producir
diagnósticos sintácticos secundarios por la recuperación de ANTLR.
`--arbol-completo` permite inspeccionar el árbol sin el resumen de consola.

## 10. Ejemplos de programas válidos e inválidos

La suite `python -m unittest discover -s tests -v` exige aceptación de
los positivos, rechazo de los negativos y comprueba tokens, precedencia,
escapes, posiciones de error y estados de salida. Ver también
[`docs/reporte_pruebas.md`](reporte_pruebas.md).

Ver la carpeta [`ejemplos/`](../ejemplos):

- `ejemplos/validos/01_carga_y_pipeline.flujo` — carga y pipeline de
  selección/filtrado.
- `ejemplos/validos/02_expresiones_basicas.flujo` — asignaciones y
  expresiones aritmético-lógicas.
- `ejemplos/validos/03_visualizacion.flujo` — reconocimiento sintáctico
  de dos instrucciones `graficar`, con y sin cláusulas opcionales.
- `ejemplos/invalidos/01_error_lexico_cadena_sin_cerrar.flujo` — error
  léxico (cadena sin cerrar).
- `ejemplos/invalidos/02_error_sintactico_falta_punto_coma.flujo` —
  error sintáctico (falta `;`).
- `ejemplos/invalidos/03_error_palabra_reservada_como_identificador.flujo`
  — error sintáctico (uso de `x`/`y` como identificador).

## 11. Decisiones de diseño y justificación

- **`;` como terminador explícito de sentencia**, en vez de depender
  de saltos de línea significativos (como en el ejemplo ilustrativo
  del enunciado): evita construir un lexer sensible a indentación o a
  la posición del salto de línea, reduciendo la complejidad léxica del
  reconocedor sin perder legibilidad, ya que el operador `|>` sigue
  permitiendo partir un pipeline en varias líneas.
- **Operadores lógicos simbólicos (`&&`, `||`, `!`)** en vez de
  palabras como "y"/"o": evita la ambigüedad con las palabras
  reservadas `x`/`y` usadas como ejes en `graficar`, y mantiene el
  conjunto de palabras reservadas más pequeño.
- **Identificadores solo ASCII**: simplifica la regla léxica de
  identificador (no requiere tratar rangos Unicode) a cambio de pedir
  nombres de columna sin tildes, una restricción menor y documentada.
- **Reconocimiento sintáctico completo de `graficar`** (los cinco
  tipos de gráfica y sus cláusulas opcionales) aunque el corte actual
  no lo ejecute: ofrece una base para el Corte 3. Actualmente todos
  los tipos requieren `x` e `y`; las necesidades de histogramas y cajas
  podrán motivar una extensión documentada antes de su ejecución.
- **Reglas con alternativas etiquetadas** (`fuenteCarga`,
  `fuentePipeline`, `fuenteExpresion`, y las etiquetas de `expresion`):
  distinguen contextos del árbol ya en el Corte 1 y facilitan escribir
  el Visitor del Corte 2.
- **Motor de datos y graficación en Python puro, sin pandas, NumPy ni
  Matplotlib**: aunque el enunciado las ofrece como apoyo opcional, el
  equipo prefiere implementar a mano la representación de tablas, las
  agregaciones, las estadísticas descriptivas y el dibujo de las
  gráficas. No cambia el alcance funcional del DSL (las mismas
  operaciones descritas en la tabla de la sección 2 del enunciado
  siguen siendo la meta), pero sí cambia el diseño interno de los
  Cortes 2 y 3 y mantiene `requirements.txt` limitado a
  `antlr4-python3-runtime`.

## 12. Plan para los próximos cortes

- **Corte 2:** implementar el Visitor sobre el árbol ya generado,
  diseñar la tabla de símbolos, y extender la gramática (de forma
  incremental, sin romper lo ya construido) con columnas calculadas
  (`crear`), agrupamiento (`agrupar por`) y agregaciones (`resumir`);
  implementar tratamiento de faltantes y exportación de resultados a CSV.
- **Corte 3:** implementar `graficar` con código propio (sin
  Matplotlib) que dibuje directamente los cinco tipos de gráfica sobre
  los datos ya agregados y exporte el resultado a PNG, completar
  la interfaz de ejecución y
  desarrollar el caso de estudio completo con el dataset de ventas.

## 13. Ver también

[`docs/conceptos_antlr.md`](conceptos_antlr.md) explica, con más
detalle del que cabe aquí, cómo `grammar/FlujoDatos.g4` se convierte
en código Python (qué genera el comando `antlr4`, de qué clases hereda
cada pieza generada) y cómo encajan entre sí `grammar/FlujoDatos.g4`,
`src/parser/` y `src/validar.py`. Es la referencia recomendada para
repasar los fundamentos de ANTLR usados en este corte.
