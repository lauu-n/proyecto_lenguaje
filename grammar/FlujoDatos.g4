grammar FlujoDatos;

// ================================================================
// NOMBRE DE LA GRAMÁTICA
// ================================================================
// Este archivo se llama FlujoDatos.
// Aquí escribimos las reglas que nuestro lenguaje va a reconocer.


// ================================================================
// REGLAS DEL PARSER
// ================================================================
// Estas reglas están en MINÚSCULA.
// Sirven para decir cómo se deben ordenar los tokens.
//
// En palabras simples:
// el lexer reconoce las palabras y símbolos.
// el parser revisa si están en el orden correcto.
//
// Ejemplo:
//
// Si escribimos:
// ventas = cargar "ventas.csv";
//
// El lexer reconoce cosas como:
// ID, '=', CARGAR, STRING, ';'
//
// Después, el parser revisa si esos tokens están en un orden
// permitido por las reglas del lenguaje.


// -------------------------
// REGLA: programa
// -------------------------
// Esta es la regla principal del programa.
//
// Dice:
// un programa tiene una o más sentencias
// y después debe llegar al final del archivo.
//
// El símbolo + significa "una o más veces".
// EOF significa "fin del archivo".
programa
    : sentencia+ EOF
    ;


// -------------------------
// REGLA: sentencia
// -------------------------
// Esta regla dice qué cosas pueden formar una sentencia.
//
// Una sentencia puede ser:
// 1. una asignación
// 2. una instrucción para graficar
//
// El ; significa que la sentencia debe terminar en punto y coma.
sentencia
    : asignacion ';'
    | sentenciaGraficar ';'
    ;


// -------------------------
// REGLA: asignacion
// -------------------------
// Esta regla permite guardar algo en una variable.
//
// Ejemplo:
// ventas = cargar "ventas.csv"
//
// Primero aparece un ID (el nombre de la variable).
// Después aparece =.
// Después aparece la fuente de datos.
asignacion
    : ID '=' fuenteDatos
    ;


// -------------------------
// REGLA: fuenteDatos
// -------------------------
// Esta regla dice de dónde pueden salir los datos.
//
// Puede ser una de estas tres cosas:
// 1. cargar un archivo CSV
// 2. hacer operaciones usando |> 
// 3. usar una expresión
//
// El símbolo | significa "o".
fuenteDatos
    : cargaCSV                     # fuenteCarga
    | ID ( PIPE operacion )+       # fuentePipeline
    | expresion                    # fuenteExpresion
    ;


// -------------------------
// REGLA: cargaCSV
// -------------------------
// Esta regla sirve para cargar un archivo.
//
// Debe aparecer la palabra "cargar"
// y después un texto entre comillas.
//
// Ejemplo:
// cargar "ventas.csv"
cargaCSV
    : CARGAR STRING
    ;


// -------------------------
// REGLA: operacion
// -------------------------
// Esta regla dice qué operaciones se pueden hacer con los datos.
//
// Por ahora hay dos:
// - seleccionar columnas
// - filtrar datos
operacion
    : seleccionOp
    | filtroOp
    ;


// -------------------------
// REGLA: seleccionOp
// -------------------------
// Esta regla sirve para escoger columnas.
//
// Debe aparecer:
// seleccionar [ columna1, columna2, columna3 ]
//
// Los corchetes [ ] forman parte de la sintaxis.
seleccionOp
    : SELECCIONAR '[' listaColumnas ']'
    ;


// -------------------------
// REGLA: filtroOp
// -------------------------
// Esta regla sirve para filtrar los datos.
//
// Debe aparecer:
// filtrar donde condicion
filtroOp
    : FILTRAR DONDE condicion
    ;


// -------------------------
// REGLA: listaColumnas
// -------------------------
// Esta regla representa una lista de nombres de columnas.
//
// Debe haber por lo menos una columna.
//
// Después pueden aparecer más columnas separadas por comas.
//
// Ejemplo:
// producto, precio, cantidad
listaColumnas
    : ID ( ',' ID )*
    ;


// -------------------------
// REGLA: condicion
// -------------------------
// Esta regla representa una condición.
//
// En este momento una condición simplemente usa una expresión.
condicion
    : expresion
    ;


// -------------------------
// REGLA: sentenciaGraficar
// -------------------------
// Esta regla reconoce una instrucción para crear una gráfica.
//
// La estructura es más o menos:
// graficar TIPO dataset x columna_horizontal y columna_vertical
//
// Además, el título es opcional.
// Y guardar la gráfica también es opcional.
//
// El ? significa "puede aparecer o puede no aparecer".
sentenciaGraficar
    : GRAFICAR tipoGrafica ID
        EJE_X ID
        EJE_Y ID
        ( TITULO STRING )?
        ( GUARDAR COMO STRING )?
    ;


// -------------------------
// REGLA: tipoGrafica
// -------------------------
// Esta regla dice qué tipos de gráficas existen.
//
// Se puede usar:
// barras
// lineas
// histograma
// dispersion
// caja
tipoGrafica
    : BARRAS
    | LINEAS
    | HISTOGRAMA
    | DISPERSION
    | CAJA
    ;


// -------------------------
// REGLA: expresion
// -------------------------
// Esta es la regla que reconoce operaciones matemáticas y lógicas.
//
// Aquí se pueden reconocer cosas como:
// -5
// !verdadero
// 2 ^ 3
// 2 * 4
// 2 + 4
// 5 > 3
// 5 == 5
// verdadero && falso
// verdadero || falso
// (2 + 3)
//
// También puede reconocer números, textos, booleanos y nombres de variables.
//
// El orden de las reglas hace que unas operaciones tengan prioridad
// sobre otras. Por ejemplo, la multiplicación va antes que la suma.
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


// -------------------------
// REGLA: literal
// -------------------------
// Un literal es un valor escrito directamente.
//
// Puede ser:
// - un número entero
// - un número decimal
// - un texto
// - verdadero o falso
literal
    : INT
    | FLOAT
    | STRING
    | BOOLEANO
    ;


// ================================================================
// REGLAS DEL LEXER
// ================================================================
// Estas reglas están en MAYÚSCULA.
//
// El lexer toma el texto que escribimos y busca palabras,
// números y símbolos.
//
// Por ejemplo:
// cargar
// 123
// "hola"
// +
// |> 
//
// Cada cosa reconocida se convierte en un TOKEN.


// -------------------------
// PALABRAS RESERVADAS
// -------------------------
// Estas reglas reconocen palabras que tienen un significado especial.
//
// Por ejemplo:
// "cargar" se convierte en el token CARGAR.
//
// Estas reglas están antes de ID para que palabras como "cargar"
// no sean confundidas con nombres de variables.
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


// -------------------------
// REGLA: PIPE
// -------------------------
// Esta regla reconoce los dos caracteres:
// |>
//
// Se usa para encadenar operaciones.
//
// Ejemplo:
// datos |> seleccionar [...]
PIPE : '|>';


// -------------------------
// REGLA: FLOAT
// -------------------------
// Esta regla reconoce números con punto decimal.
//
// Ejemplos:
// 3.14
// 10.5
// 0.25
//
// DIGITO significa un número del 0 al 9.
// El + significa que debe haber uno o más dígitos.
FLOAT
    : DIGITO+ '.' DIGITO+
    ;


// -------------------------
// REGLA: INT
// -------------------------
// Esta regla reconoce números enteros.
//
// Ejemplos:
// 1
// 25
// 100
//
// No llevan punto decimal.
INT
    : DIGITO+
    ;


// -------------------------
// REGLA: STRING
// -------------------------
// Esta regla reconoce textos escritos entre comillas.
//
// Ejemplos:
// "hola"
// "ventas.csv"
// "precio mayor a 100"
//
// Las comillas " " indican dónde empieza y termina el texto.
// No se permiten saltos de línea dentro del texto.
// Solo se admiten los escapes de comilla (\") y barra invertida (\\).
// La barra no pertenece a la alternativa de caracteres ordinarios.
STRING
    : '"' ( '\\' ["\\] | ~["\\\r\n] )* '"'
    ;


// -------------------------
// REGLA: ID
// -------------------------
// ID significa identificador.
//
// Un identificador es un nombre que podemos usar,
// por ejemplo, para una variable o una columna.
//
// Ejemplos:
// ventas
// precio
// producto1
// mi_variable
//
// Primero debe aparecer una letra o _.
// Después pueden aparecer letras, números o _.
ID
    : LETRA ( LETRA | DIGITO )*
    ;


// -------------------------
// REGLA: DIGITO
// -------------------------
// Esta regla representa un solo número del 0 al 9.
//
// "fragment" significa que esta regla es solo una ayuda
// para otras reglas. No crea un token por separado.
fragment DIGITO : [0-9];


// -------------------------
// REGLA: LETRA
// -------------------------
// Esta regla representa una letra de la A a la Z,
// en mayúscula o minúscula.
//
// También permite _.
fragment LETRA  : [a-zA-Z_];


// -------------------------
// REGLA: COMENTARIO
// -------------------------
// Esta regla reconoce comentarios.
//
// Un comentario empieza con #.
// Todo lo que aparezca después de # hasta el final de la línea
// se considera comentario.
//
// Ejemplo:
// # esto es un comentario
//
// -> skip significa que el lexer lo ignora
// y no se lo entrega al parser.
COMENTARIO
    : '#' ~[\r\n]* -> skip
    ;


// -------------------------
// REGLA: WS
// -------------------------
// WS significa "Whitespace", es decir, espacios en blanco.
//
// Aquí se reconocen:
// - espacios
// - tabulaciones
// - saltos de línea
//
// -> skip significa que se ignoran.
// Por eso no necesitamos escribir reglas en el parser
// para los espacios.
WS
    : [ \t\r\n]+ -> skip
    ;
