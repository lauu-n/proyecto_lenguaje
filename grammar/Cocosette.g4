grammar Cocosette;

// ================================================================
// REGLAS DEL PARSER
// ================================================================

programa
    : sentencia+ EOF
    ;

sentencia
    : asignacion ';'
    | cocoGraficar ';'
    | cocoGuardarCSV ';'
    | cocoImprimir ';'
    | cocoDefFuncion ';'?
    | cocoRetornar
    | cocoMientras ';'?
    | expresion ';'
    ;

asignacion
    : ID '=' cocoFuente
    ;

cocoFuente
    : cargaCSV                     # fuenteCarga
    | ID ( PIPE operacion )+       # fuentePipeline
    | expresion                    # fuenteExpresion
    ;

cargaCSV
    : COCOCARGAR STRING
    ;

// Exporta una tabla a un archivo CSV.
cocoGuardarCSV
    : COCOGUARDAR ID COMO STRING
    ;

cocoImprimir
    : COCOIMPRIMIR ( '(' expresion ')' | expresion )
    ;

cocoMientras
    : COCOMIENTRAS '('? expresion ')'? '{' sentencia* '}'
    ;

cocoDefFuncion
    : COCOFUNCION ID '(' listaParams? ')' '{' sentencia* '}'
    ;

listaParams
    : ID ( ',' ID )*
    ;

cocoRetornar
    : COCORETORNAR expresion? ';'
    ;

llamadaFuncion
    : ID '(' listaArgumentos? ')'
    ;

listaArgumentos
    : expresion ( ',' expresion )*
    ;

// Funciones disponibles para machine learning y evaluación.
cocoLlamadaML
    : cocoRegresionLineal
    | cocoRegresionPoli
    | cocoPerceptron
    | cocoCalcular
    ;

cocoRegresionLineal
    : COCOREGRESION_LINEAL '(' listaArgumentos ')'
    ;

cocoRegresionPoli
    : COCOREGRESION_POLI '(' listaArgumentos ')'
    ;

cocoPerceptron
    : COCOPERCEPTRON '(' listaArgumentos ')'
    ;

cocoCalcular
    : COCOCALCULAR '(' listaArgumentos ')'
    ;

operacion
    : cocoSeleccion
    | cocoFiltro
    | cocoCrear
    | cocoOrdenar
    | cocoRenombrar
    | cocoEliminarDuplicados
    | cocoTratarNulos
    | cocoConvertir
    | cocoAgrupar
    | cocoResumir
    ;

cocoCrear
    : COCOCREAR ID '=' expresion
    ;

cocoOrdenar
    : COCOORDENAR COCOPOR ID ( COCOASC | COCODESC )?
    ;

cocoRenombrar
    : COCORENOMBRAR ID COMO ID
    ;

cocoEliminarDuplicados
    : COCOELIMINARDUP
    ;

cocoTratarNulos
    : COCOELIMINARNULL
    | COCORELLENARNULL ID COCOCON expresion
    ;

cocoConvertir
    : COCOCONVERTIR ID COCOA tipoDato
    ;

tipoDato
    : COCOENTERO
    | COCODECIMAL
    | COCOTEXTO
    | COCOBOOLEANO
    ;

cocoAgrupar
    : COCOAGRUPAR COCOPOR '[' listaCocolumnas ']'
    ;

cocoResumir
    : COCORESUMIR asignacionAgregada ( ',' asignacionAgregada )*
    ;

asignacionAgregada
    : ID '=' funcionAgregacion '(' ID? ')'
    ;

funcionAgregacion
    : COCOSUMA
    | COCOMEDIA
    | COCOMEDIANA
    | COCOMINIMO
    | COCOMAXIMO
    | COCODESVIACIONEST
    | COCOCONTAR
    ;

cocoSeleccion
    : COCOSELECCIONAR '[' listaCocolumnas ']'
    ;

cocoFiltro
    : COCOFILTRAR COCODONDE cocondicion
    ;

listaCocolumnas
    : ID ( ',' ID )*
    ;

cocondicion
    : expresion
    ;

// La regla de graficación conserva la sintaxis de Cocosette0.
cocoGraficar
    : COCOGRAFICAR cocoGrafica tabla=ID
        ejeX colx=ID
        ( ejeY coly=ID )?
        ( COCOAJUSTE modelo=ID )?
        ( COCOTITULO titulo=STRING )?
        ( COCOETIQUETAX etx=STRING )?
        ( COCOETIQUETAY ety=STRING )?
        ( COCOLEYENDA leyenda=STRING )?
        ( COCOGUARDAR COMO ruta=STRING )?
    ;

cocoGrafica
    : COCOBARRAS
    | COCOLINEAS
    | COCOHISTOGRAMA
    | COCODISPERSION
    | COCOCAJA
    ;

// Se mantienen los predicados semánticos de Cocosette0.
ejeX
    : {self._input.LT(1).text == 'x'}? ID
    ;

ejeY
    : {self._input.LT(1).text == 'y'}? ID
    ;

expresion
    : op = ( '-' | '!' ) expresion                          # expUnaria
    | <assoc=right> expresion '^' expresion                 # expPotencia
    | expresion op = ( '*' | '/' | '%' ) expresion          # expMultiplicativa
    | expresion op = ( '+' | '-' ) expresion                # expAditiva
    | expresion op = ( '<' | '<=' | '>' | '>=' ) expresion  # expRelacional
    | expresion op = ( '==' | '!=' ) expresion              # expIgualdad
    | expresion '&&' expresion                              # expAnd
    | expresion '||' expresion                              # expOr
    | '(' expresion ')'                                     # expParentesis
    | llamadaFuncion                                        # expLlamada
    | cocoLlamadaML                                         # expLlamadaML
    | literal                                               # expLiteral
    | ID                                                    # expIdentificador
    ;

literal
    : INT
    | FLOAT
    | STRING
    | COCOBOOLEANO
    ;

// ================================================================
// REGLAS DEL LEXER
// ================================================================

COCOCARGAR        : 'cargar';
COCOSELECCIONAR   : 'seleccionar';
COCOFILTRAR       : 'filtrar';
COCODONDE         : 'donde';
COCOGRAFICAR      : 'graficar';
COCOTITULO        : 'titulo';
COCOGUARDAR       : 'guardar';
COCOIMPRIMIR      : 'imprimir' | 'mostrar';
COCOMIENTRAS      : 'mientras' | 'while';
COCOFUNCION       : 'funcion' | 'def' | 'fn';
COCORETORNAR      : 'retornar' | 'return';
COCOREGRESION_LINEAL : 'regresion_lineal';
COCOREGRESION_POLI   : 'regresion_polinomial';
COCOPERCEPTRON       : 'perceptron';
COCOCALCULAR         : 'calcular';
COMO              : 'como';
COCOBARRAS        : 'barras';
COCOLINEAS        : 'lineas';
COCOHISTOGRAMA    : 'histograma';
COCODISPERSION    : 'dispersion';
COCOCAJA          : 'caja';
COCOBOOLEANO      : 'verdadero' | 'falso';
COCOCREAR         : 'crear';
COCOORDENAR       : 'ordenar';
COCOPOR           : 'por';
COCOASC           : 'asc' | 'ascendente' | 'ascendiente';
COCODESC          : 'desc' | 'descendente' | 'descendiente';
COCORENOMBRAR     : 'renombrar';
COCOELIMINARDUP   : 'eliminar_duplicados';
COCOELIMINARNULL  : 'eliminar_nulos';
COCORELLENARNULL  : 'rellenar_nulos';
COCOCON           : 'con';
COCOCONVERTIR     : 'convertir';
COCOA             : 'a';
COCOENTERO        : 'entero';
COCODECIMAL       : 'decimal';
COCOTEXTO         : 'texto';
COCOAGRUPAR       : 'agrupar';
COCORESUMIR       : 'resumir';
COCOSUMA          : 'suma';
COCOMEDIA         : 'media';
COCOMEDIANA       : 'mediana';
COCOMINIMO        : 'minimo';
COCOMAXIMO        : 'maximo';
COCODESVIACIONEST : 'desviacion_estandar';
COCOCONTAR        : 'contar';
COCOETIQUETAX     : 'etiqueta_x';
COCOETIQUETAY     : 'etiqueta_y';
COCOLEYENDA       : 'leyenda';
COCOAJUSTE        : 'ajuste';

PIPE : '|>';

FLOAT
    : DIGITO+ '.' DIGITO+
    ;

INT
    : DIGITO+
    ;

STRING
    : '"' ( '\\"' | '\\\\' | ~["\r\n\\] )* '"'
    ;

ID
    : LETRA ( LETRA | DIGITO | '_' )*
    ;

fragment DIGITO : [0-9];
fragment LETRA  : [a-zA-Z_];

COMENTARIO
    : '#' ~[\r\n]* -> skip
    ;

COCOSPACE
    : [ \t\r\n]+ -> skip
    ;
