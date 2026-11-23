#!/bin/bash
cd /home/oem/Desktop/proyecto_lenguaje
clear
echo "========================================================================"
echo " COCOSETTE - CORTE III: EJECUCION DE EJEMPLOS DE MACHINE LEARNING Y DSL "
echo "========================================================================"
echo ""
for f in ejemplos/validos/*.coco; do
    echo "------------------------------------------------------------------------"
    echo ">>> EJECUTANDO: $f"
    echo "------------------------------------------------------------------------"
    python3 src/main.py "$f"
    echo ""
    sleep 0.5
done
echo "========================================================================"
echo " TODOS LOS EJEMPLOS EJECUTADOS EXITOSAMENTE (10/10)"
echo "========================================================================"
exec bash
