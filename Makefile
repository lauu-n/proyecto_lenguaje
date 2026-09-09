PYTHON ?= python3
ANTLR_JAR ?= tools/antlr-4.13.2-complete.jar

.PHONY: generar validar

generar:
	$(PYTHON) tools/generar.py --antlr-jar "$(ANTLR_JAR)"

# Los ejemplos negativos pasan la prueba únicamente cuando son rechazados.
validar:
	$(PYTHON) -m unittest discover -s tests -v
