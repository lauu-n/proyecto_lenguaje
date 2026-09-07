grammar FlujoDatos;

// =================================================================
// FlujoDatos — DSL para Ciencia de Datos y Visualización
// Universidad Sergio Arboleda — Lenguajes de Programación y Transducción
// Corte 1: Especificación y front-end del lenguaje
// Caso de estudio: Ventas (dominio elegido por su menor complejidad léxica)
//
// Alcance cubierto en este corte (ver docs/documento_alcance.md):
//   - Asignaciones y expresiones aritmético-lógicas básicas
//   - Carga de archivos CSV
//   - Selección de columnas
//   - Filtros con comparaciones simples
//   - Reconocimiento SINTÁCTICO de una instrucción de visualización
//     (no se ejecuta ni se genera la gráfica todavía)
//
// Fuera de alcance en este corte (planeado para Corte 2 y 3):
//   columnas calculadas, agrupamientos/agregaciones, ejecución real
//   (Visitor), exportación real a CSV/PNG, CLI completa. Esa ejecución
//   se construirá en Python puro (sin pandas/NumPy/Matplotlib, ver
//   docs/documento_alcance.md sección 2 y docs/conceptos_antlr.md).
//
// -----------------------------------------------------------------
// CÓMO LEER ESTE ARCHIVO (para repasar los fundamentos de ANTLR)
// -----------------------------------------------------------------
// Este .g4 es una GRAMÁTICA COMBINADA: reglas de parser y reglas de
// lexer conviven en el mismo archivo porque este proyecto tiene un
// único lexer para un único parser (ANTLR también permite separarlos
// en dos archivos —.g4 de lexer y .g4 de parser— cuando un mismo
// lexer alimenta a varios parsers distintos; no es nuestro caso).
//
// Este archivo NO contiene ningún algoritmo de análisis léxico ni
// sintáctico: solo DECLARA reglas. El comando `antlr4` (ver Makefile,
// target `generar`) lee este archivo y GENERA tres/cuatro archivos
// Python nuevos dentro de src/parser/ (no se versionan, ver
// .gitignore, porque son reproducibles):
//
//   grammar/FlujoDatos.g4  --(antlr4 -Dlanguage=Python3 -visitor)-->
//       src/parser/FlujoDatosLexer.py    clase FlujoDatosLexer(Lexer)
//       src/parser/FlujoDatosParser.py   clase FlujoDatosParser(Parser)
//       src/parser/FlujoDatosVisitor.py  clase FlujoDatosVisitor(ParseTreeVisitor)
//       src/parser/FlujoDatosListener.py clase FlujoDatosListener(ParseTreeListener)
//
// Las clases base entre paréntesis (Lexer, Parser, ParseTreeVisitor,
// ParseTreeListener) NO las escribimos nosotros: vienen del paquete
// `antlr4-python3-runtime` (ver requirements.txt) y contienen el
// algoritmo real de reconocimiento (simulación de autómatas). El
// código generado a partir de ESTE archivo solo llena esas clases
// base con las reglas concretas de FlujoDatos. Ese es el sentido de
// "herencia" en este proyecto: FlujoDatosLexer no reimplementa cómo
// tokenizar, hereda ese comportamiento de Lexer y solo aporta la
// tabla de reglas léxicas de abajo.
//
// Mapa de dependencias entre archivos (quién apunta a quién):
//
//   grammar/FlujoDatos.g4  (este archivo, lo escribimos nosotros)
//         |  se procesa con el comando `antlr4` (ver Makefile)
//         v
//   src/parser/FlujoDatos*.py  (generado, no se edita a mano)
//         |  se importa con `from FlujoDatosLexer import ...`
//         v
//   src/validar.py  (lo escribimos nosotros, ver sus comentarios)
//
// Ver docs/conceptos_antlr.md para una explicación más detallada,
// con tabla de clases/herencia y diagrama del flujo completo.
// =================================================================


// -----------------------------------------------------------------
// REGLAS DEL PARSER
// -----------------------------------------------------------------
// Convención de ANTLR: una regla que empieza en minúscula es una
// REGLA DE PARSER. Cada una se convierte en un MÉTODO de
// FlujoDatosParser (p. ej. la regla `programa` se vuelve el método
// `parser.programa()`) que, al ejecutarse, consume tokens del
// CommonTokenStream y devuelve un objeto "Context" (p. ej.
// `ProgramaContext`) representando ese nodo del árbol de análisis.
// Cada símbolo no terminal que aparece dentro de una regla (por
// ejemplo `sentencia` dentro de `programa`) se convierte en un nodo
// hijo de ese Context, y así se arma el árbol completo.

// La regla raíz: un programa es una o más sentencias, y EOF exige
// que el parser llegue hasta el final real del archivo (si no,
// cualquier texto sobrante después de una sentencia válida quedaría
// silenciosamente sin reconocer, en vez de reportarse como error).
programa
    : sentencia+ EOF
    ;

// Una sentencia es una asignación o una instrucción de graficar,
// siempre terminada en ';' (ver justificación del ';' explícito en
// docs/documento_alcance.md, sección 11).
sentencia
    : asignacion ';'
    | sentenciaGraficar ';'
    ;

// ---- Asignaciones: carga de datos, pipelines y expresiones ----
asignacion
    : ID '=' fuenteDatos
    ;

// Nota sobre las etiquetas "# nombre" que aparecen después de cada
// alternativa (# fuenteCarga, # fuentePipeline, # fuenteExpresion):
// SIN esas etiquetas, ANTLR generaría una única clase
// `FuenteDatosContext` con métodos opcionales para las tres
// alternativas, obligando a preguntar en tiempo de ejecución cuál de
// ellas se usó (p. ej. `if ctx.cargaCSV() is not None: ...`). CON
// las etiquetas, ANTLR genera una subclase de contexto POR
// alternativa (FuenteCargaContext, FuentePipelineContext,
// FuenteExpresionContext, cada una heredando de FuenteDatosContext),
// y el Visitor que se implementará en el Corte 2 recibe
// automáticamente un método distinto por cada caso
// (visitFuenteCarga, visitFuentePipeline, visitFuenteExpresion) sin
// tener que preguntar nada a mano. Es puro azúcar sintáctico de
// ANTLR sobre el mismo BNF de siempre, no cambia lo que el lenguaje
// reconoce.
fuenteDatos
    : cargaCSV                     # fuenteCarga
    | ID ( PIPE operacion )+       # fuentePipeline
    | expresion                    # fuenteExpresion
    ;

cargaCSV
    : CARGAR STRING
    ;

operacion
    : seleccionOp
    | filtroOp
    ;

seleccionOp
    : SELECCIONAR '[' listaColumnas ']'
    ;

filtroOp
    : FILTRAR DONDE condicion
    ;

listaColumnas
    : ID ( ',' ID )*
    ;

condicion
    : expresion
    ;

// ---- Visualización: solo reconocimiento sintáctico en Corte 1 ----
sentenciaGraficar
    : GRAFICAR tipoGrafica ID
        EJE_X ID
        EJE_Y ID
        ( TITULO STRING )?
        ( GUARDAR COMO STRING )?
    ;

tipoGrafica
    : BARRAS
    | LINEAS
    | HISTOGRAMA
    | DISPERSION
    | CAJA
    ;

// ---- Expresiones aritmético-lógicas (precedencia de mayor a menor) ----
// Esta es una regla LEFT-RECURSIVE: `expresion` aparece dentro de sus
// propias alternativas (p. ej. `expresion op expresion`). ANTLR4
// detecta esto y lo reescribe internamente como una jerarquía de
// reglas sin recursión izquierda directa (equivalente al EBNF de la
// sección 7 del documento de alcance), sin que tengamos que escribir
// esa jerarquía a mano. La regla fundamental para leer esta lista es:
// EL ORDEN DE LAS ALTERNATIVAS DEFINE LA PRECEDENCIA, de mayor a
// menor (la primera alternativa liga más fuerte). Por eso `*` está
// antes que `+`, y `+` está antes que `<`, etc. `<assoc=right>` es la
// única excepción explícita: sin ella, `^` asociaría a la izquierda
// por defecto, y `2 ^ 3 ^ 2` se leería como `(2^3)^2` en vez de
// `2^(3^2)`. Las etiquetas `op = ( '+' | '-' )` guardan en `ctx.op`
// cuál de los dos símbolos hizo match, dato que el Visitor del Corte
// 2 necesitará para decidir qué operación ejecutar.
expresion
    : op = ( '-' | '!' ) expresion                     # expUnaria
    | <assoc=right> expresion '^' expresion            # expPotencia
    | expresion op = ( '*' | '/' | '%' ) expresion      # expMultiplicativa
    | expresion op = ( '+' | '-' ) expresion            # expAditiva
    | expresion op = ( '<' | '<=' | '>' | '>=' ) expresion  # expRelacional
    | expresion op = ( '==' | '!=' ) expresion          # expIgualdad
    | expresion '&&' expresion                          # expAnd
    | expresion '||' expresion                          # expOr
    | '(' expresion ')'                                 # expParentesis
    | literal                                           # expLiteral
    | ID                                                 # expIdentificador
    ;

literal
    : INT
    | FLOAT
    | STRING
    | BOOLEANO
    ;


// -----------------------------------------------------------------
// REGLAS DEL LEXER
// -----------------------------------------------------------------
// Convención de ANTLR: una regla que empieza en MAYÚSCULA es una
// REGLA DE LEXER (también llamada "token"). A diferencia de las
// reglas de parser, estas no producen nodos del árbol: el lexer
// consume caracteres del archivo fuente y emite una secuencia plana
// de tokens (par tipo+texto, p. ej. `CARGAR "cargar"`), que luego
// CommonTokenStream le entrega al parser de a uno. El parser nunca
// ve caracteres sueltos, solo tokens ya reconocidos.

// ---- Palabras reservadas (SIEMPRE antes de ID: gana por orden ----
// ---- ante empates de longitud en la coincidencia del lexer)    ----
// Regla de desempate del lexer de ANTLR: si dos reglas léxicas
// pueden reconocer el mismo texto con la misma longitud (p. ej.
// "cargar" calza tanto con CARGAR como, letra por letra, con el
// patrón de ID), gana la regla escrita PRIMERO en el archivo. Por
// eso todas las palabras reservadas están declaradas antes que ID:
// si ID fuera la primera, "cargar" se tokenizaría como un
// identificador cualquiera y la palabra reservada nunca se
// reconocería.
CARGAR       : 'cargar';
SELECCIONAR  : 'seleccionar';
FILTRAR      : 'filtrar';
DONDE        : 'donde';
GRAFICAR     : 'graficar';
TITULO       : 'titulo';
GUARDAR      : 'guardar';
COMO         : 'como';
BARRAS       : 'barras';
LINEAS       : 'lineas';
HISTOGRAMA   : 'histograma';
DISPERSION   : 'dispersion';
CAJA         : 'caja';
EJE_X        : 'x';
EJE_Y        : 'y';
BOOLEANO     : 'verdadero' | 'falso';

// ---- Operador de encadenamiento (pipeline) ----
PIPE : '|>';

// ---- Literales numéricos y de texto ----
// Importante: FLOAT está declarado ANTES que INT. Ante una entrada
// como "3.14", ambas reglas podrían empezar a calzar con el prefijo
// "3", pero solo FLOAT calza con la cadena completa (mayor longitud
// gana siempre en el lexer de ANTLR, independientemente del orden;
// el orden solo desempata longitudes IGUALES). Aun así se mantiene
// este orden por legibilidad y porque es el hábito seguro en ANTLR.
FLOAT
    : DIGITO+ '.' DIGITO+
    ;

INT
    : DIGITO+
    ;

// El '?' después de '*' hace la repetición NO codiciosa (non-greedy):
// sin él, el motor probaría primero consumir hasta la ÚLTIMA comilla
// del archivo. `~["\r\n]` además prohíbe saltos de línea dentro de
// una cadena (restricción documentada en docs/documento_alcance.md).
STRING
    : '"' ( '\\"' | ~["\r\n] )*? '"'
    ;

// ---- Identificadores (solo ASCII: ver justificación en docs) ----
ID
    : LETRA ( LETRA | DIGITO | '_' )*
    ;

// Un `fragment` NO es un token: es una pieza reutilizable de patrón
// que otras reglas léxicas pueden citar (como DIGITO y LETRA dentro
// de FLOAT, INT e ID), pero que nunca se emite por sí sola como
// token independiente. Sirve para no repetir el mismo rango de
// caracteres en varias reglas.
fragment DIGITO : [0-9];
fragment LETRA  : [a-zA-Z_];

// ---- Comentarios y espacios en blanco (se descartan) ----
// `-> skip` le dice al lexer: reconoce este patrón como token, pero
// no lo pases al parser. Por eso el parser nunca tiene que lidiar
// con comentarios ni con espacios/tabs/saltos de línea; ya llegaron
// filtrados desde el lexer.
COMENTARIO
    : '#' ~[\r\n]* -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
