"""Validador de sintaxis para el lenguaje Cocosette.

Este script toma uno o mas archivos .coco y reporta si cada uno es
lexica y sintacticamente valido segun la gramatica grammar/Cocosette.g4.
"""

import os
import sys

sys.path.append("src/parser")
sys.path.append("src")
sys.path.append("parser")

from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener

try:
    from CocosetteLexer import CocosetteLexer
    from CocosetteParser import CocosetteParser
except ImportError:
    print("No se encontro el lexer/parser generado por ANTLR.")
    print("Ejecuta primero:")
    print("  make generar")
    print("  (equivale a: cd grammar && antlr4 -Dlanguage=Python3 -visitor -o ../src/parser Cocosette.g4)")
    sys.exit(1)


class ColectorDeErrores(ErrorListener):
    """Guarda los errores que encuentre el lexer o el parser con linea y columna."""

    def __init__(self):
        super().__init__()
        self.errores = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errores.append(f"  linea {line}, columna {column}: {msg}")


def validar_archivo(ruta: str) -> bool:
    """Valida un unico archivo fuente .coco."""
    entrada = FileStream(ruta, encoding="utf-8")

    lexer = CocosetteLexer(entrada)
    errores_lexicos = ColectorDeErrores()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errores_lexicos)

    tokens = CommonTokenStream(lexer)

    parser = CocosetteParser(tokens)
    errores_sintacticos = ColectorDeErrores()
    parser.removeErrorListeners()
    parser.addErrorListener(errores_sintacticos)

    arbol = parser.programa()

    errores = errores_lexicos.errores + errores_sintacticos.errores
    if errores:
        print(f"[INVALIDO] {ruta}")
        for err in errores:
            print(err)
        return False

    resumen_arbol = arbol.toStringTree(recog=parser)
    if len(resumen_arbol) > 90:
        resumen_arbol = resumen_arbol[:90] + " ..."
    print(f"[VALIDO]   {ruta}")
    print(f"           arbol: {resumen_arbol}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 src/validar.py <archivo1.coco> [archivo2.coco ...]")
        sys.exit(1)

    resultados = [validar_archivo(ruta) for ruta in sys.argv[1:]]
    total = len(resultados)
    validos = sum(resultados)
    print(f"\n{validos}/{total} archivo(s) sintacticamente validos")


if __name__ == "__main__":
    main()
