grammar DSL;

// Regla de entrada
programa    : sentencia* EOF ;

sentencia   : asignacion ;

asignacion  : ID '=' expresion ;

expresion   : expresion op=('*'|'/') expresion   # MulDiv
            | expresion op=('+'|'-') expresion   # SumaResta
            | '(' expresion ')'                  # Parentesis
            | NUMBER                             # NumeroLiteral
            | STRING                             # CadenaLiteral
            | ID                                 # Identificador
            ;

// Léxico
ID          : [a-zA-Z_][a-zA-Z_0-9]* ;
NUMBER      : [0-9]+ ('.' [0-9]+)? ;
STRING      : '"' (~["\r\n])* '"' ;
WS          : [ \t\r\n]+ -> skip ;
COMENTARIO  : '#' ~[\r\n]* -> skip ;
