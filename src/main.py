"""Punto de entrada principal para el lenguaje Cocosette.

Uso:
  python3 src/main.py <archivo.coco>
"""

import os
import sys

# Agregar carpetas de modulos al path de Python
sys.path.append("src/parser")
sys.path.append("src")
sys.path.append("parser")

from antlr4 import CommonTokenStream, InputStream
from CocosetteLexer import CocosetteLexer
from CocosetteParser import CocosetteParser
from visitor import InterpreteVisitor


def ejecutar_archivo(ruta_archivo):
    """Lee un archivo .coco y lo ejecuta usando el Visitor."""
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontro el archivo: '{ruta_archivo}'")

    # 1. Leer el archivo con codigo fuente
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        codigo_fuente = f.read()

    # Imprimir el codigo fuente tal cual y los 3 guiones separadores
    print(codigo_fuente.strip())
    print("---")

    # 2. Analisis lexico y sintactico con ANTLR
    flujo_entrada = InputStream(codigo_fuente)
    lexer = CocosetteLexer(flujo_entrada)
    tokens = CommonTokenStream(lexer)
    parser = CocosetteParser(tokens)
    arbol = parser.programa()

    # 3. Ejecucion semantica con el Visitor
    visitor = InterpreteVisitor()
    visitor.visitPrograma(arbol)

    print("\nEjecucion exitosa.")
    return visitor.memoria


def main():
    if len(sys.argv) < 2:
        print("Uso del interprete Cocosette:")
        print("  python3 src/main.py <archivo.coco>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]
    try:
        ejecutar_archivo(ruta_archivo)
    except Exception as error:
        print(f"\nError en la ejecucion: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
