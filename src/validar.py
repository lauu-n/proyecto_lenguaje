#!/usr/bin/env python3
"""
Script de validación léxica y sintáctica para el DSL FlujoDatos (Corte 1).

Este script NO ejecuta los programas del DSL (eso corresponde a los
Cortes 2 y 3, cuando exista el Visitor). Su único propósito es construir
el árbol de análisis sintáctico y reportar errores léxicos/sintácticos
con línea y columna, como evidencia de que el front-end del lenguaje
reconoce programas correctos y rechaza programas incorrectos.

Uso:
    python3 src/validar.py ejemplos/validos/*.flujo
    python3 src/validar.py ejemplos/invalidos/*.flujo
    python3 src/validar.py ruta/a/un/archivo.flujo

Requisito previo (una sola vez, o cada vez que cambie la gramática):
    make generar
    # equivale a: cd grammar && antlr4 -Dlanguage=Python3 -visitor -o ../src/parser FlujoDatos.g4

y tener instalado antlr4-python3-runtime (ver requirements.txt).

-------------------------------------------------------------------
GUÍA DE LECTURA: qué archivo apunta a cuál, y quién hereda de quién
-------------------------------------------------------------------
Este archivo se apoya en dos "capas" de código que NO viven aquí:

1. La librería `antlr4` (paquete `antlr4-python3-runtime`, instalado
   por pip, ver requirements.txt). Es código de terceros, distribuido
   por el proyecto ANTLR, con el algoritmo genérico de tokenización y
   parseo. De ahí importamos piezas genéricas y reutilizables para
   CUALQUIER gramática, no solo la nuestra: `FileStream` (lee un
   archivo de texto), `CommonTokenStream` (almacena/entrega tokens al
   parser) y `ErrorListener` (clase base para reaccionar a errores).

2. `FlujoDatosLexer` y `FlujoDatosParser` (carpeta src/parser/, NO
   incluida en el repositorio: se regenera con `make generar`, ver
   .gitignore). Estas clases SÍ son específicas de nuestro lenguaje,
   pero nosotros no las escribimos a mano: ANTLR las genera a partir
   de grammar/FlujoDatos.g4. Por herencia:
       FlujoDatosLexer(Lexer)   -> Lexer viene de antlr4 (capa 1)
       FlujoDatosParser(Parser) -> Parser viene de antlr4 (capa 1)
   Es decir, la clase genérica `Lexer` de antlr4 aporta el algoritmo
   de reconocimiento; `FlujoDatosLexer` solo añade la tabla de reglas
   léxicas concretas (CARGAR, ID, STRING, ...) definidas en el .g4.
   Ver docs/conceptos_antlr.md para el mapa completo con diagrama.

Con eso, el flujo de este script es:

    archivo.flujo
        -> FileStream                (lee el texto)
        -> FlujoDatosLexer           (texto -> tokens)
        -> CommonTokenStream         (guarda/entrega los tokens)
        -> FlujoDatosParser.programa()  (tokens -> árbol de análisis)
"""
import sys
from pathlib import Path

# Capa 1: piezas genéricas del runtime de ANTLR (no específicas de
# FlujoDatos). `ErrorListener` es la clase base que reemplazamos más
# abajo con ColectorDeErrores.
from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

# Capa 2: el lexer y el parser generados a partir de grammar/FlujoDatos.g4.
# Como esos archivos no están en el repositorio (se regeneran con
# `make generar`), primero hay que agregar src/parser/ al sys.path
# para que Python los encuentre al hacer el import de abajo.
sys.path.append(str(Path(__file__).resolve().parent / "parser"))

try:
    # Estos dos imports fallan si todavía no se ejecutó `make generar`,
    # porque src/parser/FlujoDatosLexer.py y FlujoDatosParser.py aún no
    # existen como archivos físicos en disco.
    from FlujoDatosLexer import FlujoDatosLexer
    from FlujoDatosParser import FlujoDatosParser
except ImportError:
    print("No se encontro el lexer/parser generado por ANTLR.")
    print("Ejecuta primero:")
    print("  make generar")
    print("  (equivale a: cd grammar && antlr4 -Dlanguage=Python3 -visitor -o ../src/parser FlujoDatos.g4)")
    sys.exit(1)


class ColectorDeErrores(ErrorListener):
    """Hereda de `antlr4.error.ErrorListener.ErrorListener` (capa 1).

    Por defecto, tanto FlujoDatosLexer como FlujoDatosParser usan un
    `ConsoleErrorListener` que simplemente imprime los errores por
    stderr y sigue de largo. Aquí escribimos nuestra propia subclase
    que SOBREESCRIBE (override) el método `syntaxError`, el único que
    ANTLR invoca automáticamente cada vez que el lexer o el parser
    encuentran algo que no reconocen. En vez de imprimir directo,
    guardamos el mensaje (con línea y columna) en una lista, para
    poder decidir nosotros mismos qué hacer con esos errores más abajo
    en `validar_archivo`.
    """

    def __init__(self):
        super().__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errores.append(f"  linea {line}, columna {column}: {msg}")


def validar_archivo(ruta: str) -> bool:
    # 1) FileStream (antlr4, capa 1): lee el archivo .flujo como texto.
    entrada = FileStream(ruta, encoding="utf-8")

    # 2) FlujoDatosLexer (generado, capa 2): recorre el texto caracter
    #    a caracter y produce tokens según las reglas léxicas del .g4
    #    (CARGAR, ID, STRING, INT, etc.). Le quitamos su listener de
    #    errores por defecto y le ponemos el nuestro.
    lexer = FlujoDatosLexer(entrada)
    errores_lexicos = ColectorDeErrores()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errores_lexicos)

    # 3) CommonTokenStream (antlr4, capa 1): actúa de buffer entre el
    #    lexer y el parser, entregando tokens uno a uno bajo demanda.
    tokens = CommonTokenStream(lexer)

    # 4) FlujoDatosParser (generado, capa 2): consume el stream de
    #    tokens y aplica las reglas del parser (programa, sentencia,
    #    expresion, ...) para construir el árbol de análisis.
    parser = FlujoDatosParser(tokens)
    errores_sintacticos = ColectorDeErrores()
    parser.removeErrorListeners()
    parser.addErrorListener(errores_sintacticos)

    # `programa()` es el método generado a partir de la regla raíz
    # `programa` del .g4 (ver comentarios allí). Devuelve un
    # `ProgramaContext`: la raíz del árbol de análisis sintáctico.
    arbol = parser.programa()

    errores = errores_lexicos.errores + errores_sintacticos.errores
    if errores:
        print(f"[INVALIDO] {ruta}")
        for err in errores:
            print(err)
        return False

    # toStringTree() imprime el árbol en formato LISP (paréntesis
    # anidados); es solo para inspección rápida en consola, no es una
    # estructura que se vaya a reutilizar en cortes futuros.
    resumen_arbol = arbol.toStringTree(recog=parser)
    if len(resumen_arbol) > 90:
        resumen_arbol = resumen_arbol[:90] + " ..."
    print(f"[VALIDO]   {ruta}")
    print(f"           arbol: {resumen_arbol}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 src/validar.py <archivo1.flujo> [archivo2.flujo ...]")
        sys.exit(1)

    resultados = [validar_archivo(ruta) for ruta in sys.argv[1:]]
    total = len(resultados)
    validos = sum(resultados)
    print(f"\n{validos}/{total} archivo(s) sintacticamente validos")


if __name__ == "__main__":
    main()
