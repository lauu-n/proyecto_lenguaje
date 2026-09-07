CARPETA_GRAMATICA = grammar
GRAMATICA         = FlujoDatos.g4

# Misma carpeta de salida (src/parser), vista desde dos directorios de
# trabajo distintos: "generar" se ejecuta desde dentro de grammar/,
# "limpiar" y "validar" se ejecutan desde la raiz del proyecto.
SALIDA_DESDE_GRAMATICA = ../src/parser
SALIDA_DESDE_RAIZ      = src/parser

.PHONY: generar validar limpiar

# Importante: nos movemos a grammar/ antes de invocar antlr4. Si se
# invoca "antlr4 -o src/parser grammar/FlujoDatos.g4" desde la raiz,
# ANTLR replica la ruta relativa del .g4 dentro de la salida y termina
# creando src/parser/grammar/... en vez de dejar los archivos
# directamente en src/parser/.
generar:
	cd $(CARPETA_GRAMATICA) && antlr4 -Dlanguage=Python3 -visitor -o $(SALIDA_DESDE_GRAMATICA) $(GRAMATICA)

validar:
	python3 src/validar.py ejemplos/validos/*.flujo
	python3 src/validar.py ejemplos/invalidos/*.flujo

limpiar:
	# ! -name '__init__.py': ese archivo no es generado, esta versionado
	# a mano (explica el proposito de la carpeta) y el patron *.py de
	# abajo lo borraria si no se excluye explicitamente.
	find $(SALIDA_DESDE_RAIZ) -type f ! -name '__init__.py' -delete
	rm -rf $(SALIDA_DESDE_RAIZ)/__pycache__
