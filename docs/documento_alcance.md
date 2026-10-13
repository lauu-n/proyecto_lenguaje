# Documento de alcance — DSL `Cocosette`

**Curso:** Lenguajes de Programación y Transducción  
**Proyecto:** Lenguaje de Dominio Específico para Ciencia de Datos y Visualización  
**Fase:** Corte 1 y Corte 2 (Especificación, front-end y procesamiento de datos)  
**Caso de estudio:** Ventas  

---

## 1. Descripción general y dominio seleccionado

`Cocosette` es un lenguaje de dominio específico (DSL) declarativo, basado en encadenamiento de operaciones (`|>`), diseñado para describir flujos reproducibles de carga, preparación, transformación, análisis y visualización de datos sin escribir directamente código en Python.

El enunciado del proyecto sugiere seis dominios posibles para el caso de estudio final: ventas, movilidad, datos ambientales, educación, salud pública y telecomunicaciones. Se seleccionó **ventas** por tener la **menor complejidad léxica**:

| Dominio | Por qué se descartó (mayor complejidad léxica) |
|---|---|
| Movilidad | Requiere coordenadas geoespaciales y formatos de fecha/hora combinados |
| Datos ambientales | Requiere unidades científicas (ppm, °C, µg/m³) y notación con símbolos adicionales |
| Educación | Requiere escalas de calificación heterogéneas entre instituciones |
| Salud pública | Requiere codificación clínica y vocabulario sensible |
| Telecomunicaciones | Requiere unidades técnicas compuestas (Mbps, ms de latencia) |
| **Ventas (elegido)** | Solo usa literales numéricos, cadenas de texto y fechas como texto plano; sin unidades ni notación especializada |

---

## 2. Usuarios, entradas, salidas y restricciones

- **Usuarios:** Estudiantes o analistas que deseen describir un flujo de análisis de datos de ventas de manera compacta y declarativa.
- **Entradas:** Archivos fuente con extensión `.coco` (programas del DSL) y archivos CSV de datos tabulares (ej. `datos/ventas.csv`).
- **Salidas:**
  - Árbol de análisis sintáctico y diagnósticos de error con número de línea y columna.
  - Tablas procesadas en memoria, resúmenes estadísticos y exportación de archivos CSV a la carpeta `salidas/`.
- **Restricciones de diseño:**
  - Los identificadores solo admiten caracteres ASCII (`a-z`, `A-Z`, dígitos y `_`), sin tildes ni "ñ".
  - `x` y `y` son palabras reservadas (ejes de gráficos) y no pueden usarse como identificadores sueltos.
  - Las cadenas de texto no admiten saltos de línea sin cerrar.
  - Cada sentencia termina obligatoriamente en punto y coma (`;`).
  - **Sin librerías externas de análisis o graficación (sin pandas, NumPy ni Matplotlib):** El motor de datos (`Tabla`) y la memoria de ejecución (`MemoriaEjecucion`) se implementan desde cero en Python puro utilizando únicamente la biblioteca estándar (`csv`, `math`). El paquete `antlr4-python3-runtime` se utiliza únicamente para el lexer/parser por requisito de la asignatura.

---

## 3. Catálogo de Palabras Reservadas y Tokens

El lenguaje utiliza una convención interna de tokens temáticos con el prefijo `COCO*`, manteniendo palabras clave en español legibles para el usuario:

| Palabra en el DSL | Token interno | Uso |
|---|---|---|
| `cargar` | `COCOCARGAR` | Cargar un archivo CSV |
| `seleccionar` | `COCOSELECCIONAR` | Proyección de columnas dentro de un pipeline |
| `filtrar` | `COCOFILTRAR` | Filtrado de filas condicional |
| `donde` | `COCODONDE` | Introduce la condición lógica de un filtro |
| `crear` | `COCOCREAR` | Creación de columnas calculadas (Corte 2) |
| `ordenar` | `COCOORDENAR` | Ordenamiento de registros (Corte 2) |
| `por` | `COCOPOR` | Cláusula para ordenar o agrupar |
| `asc`, `ascendente` | `COCOASC` | Orden ascendente |
| `desc`, `descendente` | `COCODESC` | Orden descendente |
| `renombrar` | `COCORENOMBRAR` | Renombrar una columna existente (Corte 2) |
| `eliminar_duplicados` | `COCOELIMINARDUP` | Eliminación de filas repetidas (Corte 2) |
| `eliminar_nulos` | `COCOELIMINARNULL` | Descarte de filas con campos vacíos (Corte 2) |
| `rellenar_nulos` | `COCORELLENARNULL` | Reemplazo de nulos por un valor (Corte 2) |
| `con` | `COCOCON` | Acompaña a `rellenar_nulos` |
| `convertir` | `COCOCONVERTIR` | Casteo de tipo de columna (Corte 2) |
| `a` | `COCOA` | Acompaña a `convertir` |
| `entero`, `decimal`, `texto`, `booleano` | `COCOENTERO`, etc. | Tipos de datos destino para conversión |
| `agrupar` | `COCOAGRUPAR` | Agrupamiento por categorías (Corte 2) |
| `resumir` | `COCORESUMIR` | Cálculo de agregaciones sobre grupos (Corte 2) |
| `suma`, `media`, `mediana`, `minimo`, `maximo`, `desviacion_estandar`, `contar` | `COCOSUMA`, etc. | Funciones de agregación estadística (Corte 2) |
| `guardar` | `COCOGUARDAR` | Exportación de resultados a CSV o imagen de gráfica |
| `como` | `COMO` | Acompaña a `guardar` |
| `graficar` | `COCOGRAFICAR` | Declaración de visualización (Corte 3) |
| `barras`, `lineas`, `histograma`, `dispersion`, `caja` | `COCOBARRAS`, etc. | Tipos de gráficos admitidos |
| `x`, `y` | `EJE_X`, `EJE_Y` | Especificación de ejes para gráficos |
| `titulo` | `COCOTITULO` | Título opcional de gráficos |
| `verdadero`, `falso` | `COCOBOOLEANO` | Literales lógicos |

---

## 4. Operadores, Precedencia y Asociatividad

1. `( - , ! )` — Unarios prefijos (mayor precedencia, agrupan a la derecha).
2. `^` — Potencia (asociatividad a la derecha).
3. `* , / , %` — Multiplicativos (asociatividad a la izquierda).
4. `+ , -` — Aditivos (asociatividad a la izquierda).
5. `< , <= , > , >=` — Relacionales.
6. `== , !=` — Igualdad.
7. `&&` — Conjunción lógica (AND).
8. `||` — Disyunción lógica (OR, menor precedencia).

---

## 5. Gramática Formal (EBNF)

```ebnf
programa          ::= sentencia { sentencia } EOF ;
sentencia         ::= asignacion ";" | cocoGraficar ";" | cocoGuardarCSV ";" ;

asignacion        ::= IDENTIFICADOR "=" cocoFuente ;
cocoFuente        ::= cargaCSV | IDENTIFICADOR ( "|>" operacion )+ | expresion ;
cargaCSV          ::= "cargar" CADENA ;
cocoGuardarCSV    ::= "guardar" IDENTIFICADOR "como" CADENA ;

operacion         ::= cocoSeleccion
                    | cocoFiltro
                    | cocoCrear
                    | cocoOrdenar
                    | cocoRenombrar
                    | cocoEliminarDuplicados
                    | cocoTratarNulos
                    | cocoConvertir
                    | cocoAgrupar
                    | cocoResumir ;

cocoSeleccion     ::= "seleccionar" "[" listaColumnas "]" ;
cocoFiltro        ::= "filtrar" "donde" expresion ;
cocoCrear         ::= "crear" IDENTIFICADOR "=" expresion ;
cocoOrdenar       ::= "ordenar" "por" IDENTIFICADOR [ "asc" | "desc" | "ascendente" | "descendente" ] ;
cocoRenombrar     ::= "renombrar" IDENTIFICADOR "como" IDENTIFICADOR ;
cocoEliminarDuplicados ::= "eliminar_duplicados" ;
cocoTratarNulos   ::= "eliminar_nulos" | "rellenar_nulos" IDENTIFICADOR "con" expresion ;
cocoConvertir     ::= "convertir" IDENTIFICADOR "a" tipoDato ;
tipoDato          ::= "entero" | "decimal" | "texto" | "booleano" ;
cocoAgrupar       ::= "agrupar" "por" "[" listaColumnas "]" ;
cocoResumir       ::= "resumir" asignacionAgregada { "," asignacionAgregada } ;
asignacionAgregada::= IDENTIFICADOR "=" funcionAgregacion "(" [ IDENTIFICADOR ] ")" ;
funcionAgregacion ::= "suma" | "media" | "mediana" | "minimo" | "maximo" | "desviacion_estandar" | "contar" ;

listaColumnas     ::= IDENTIFICADOR { "," IDENTIFICADOR } ;

cocoGraficar      ::= "graficar" tipoGrafica IDENTIFICADOR
                        "x" IDENTIFICADOR
                        "y" IDENTIFICADOR
                        [ "titulo" CADENA ]
                        [ "guardar" "como" CADENA ] ;
tipoGrafica       ::= "barras" | "lineas" | "histograma" | "dispersion" | "caja" ;

expresion         ::= expOr ;
expOr             ::= expAnd { "||" expAnd } ;
expAnd            ::= expIgualdad { "&&" expIgualdad } ;
expIgualdad       ::= expRelacional { ( "==" | "!=" ) expRelacional } ;
expRelacional     ::= expAditiva { ( "<" | "<=" | ">" | ">=" ) expAditiva } ;
expAditiva        ::= expMultiplicativa { ( "+" | "-" ) expMultiplicativa } ;
expMultiplicativa ::= expPotencia { ( "*" | "/" | "%" ) expPotencia } ;
expPotencia       ::= expUnaria [ "^" expPotencia ] ;
expUnaria         ::= ( "-" | "!" ) expUnaria | expPrimaria ;
expPrimaria       ::= literal | IDENTIFICADOR | "(" expresion ")" ;

literal           ::= ENTERO | DECIMAL | CADENA | BOOLEANO ;
BOOLEANO          ::= "verdadero" | "falso" ;
```

---

## 6. Manejo de Errores

El DSL implementa detección y reporte en tres capas:
1. **Léxico:** Caracteres desconocidos o cadenas no terminadas (`ColectorDeErrores` en `src/validar.py`).
2. **Sintáctico:** Estructura inválida, falta de punto y coma o uso de palabras reservadas como variables.
3. **Semántico (Corte 2):** Variables no declaradas (`MemoriaEjecucion`), columnas inexistentes en la tabla (`Tabla._validar_columnas`) o incompatibilidad de tipos en operaciones.
