# Reporte de pruebas — DSL Cocosette

## Alcance de las Pruebas

Se valida el front-end del lenguaje (reconocimiento léxico y sintáctico) y la base del motor de ejecución del Corte 2, utilizando los casos de prueba provistos en `ejemplos/validos/` y `ejemplos/invalidos/`.

```bash
make validar
```

---

## Resultados Observados

### 1. Pruebas Positivas (Programas Válidos)

| Archivo | Caso comprobado | Resultado |
|---|---|---|
| `ejemplos/validos/01_carga_y_pipeline.coco` | Carga de CSV, selección de columnas y filtrado lógico con `&&`. | **[VALIDO]** Árbol sintáctico generado sin errores. |
| `ejemplos/validos/02_expresiones_basicas.coco` | Asignaciones, precedencia de operadores aritméticos (`+`, `*`, `^`) y booleanos. | **[VALIDO]** Árbol sintáctico generado sin errores. |
| `ejemplos/validos/03_visualizacion.coco` | Reconocimiento sintáctico de `graficar` (con y sin cláusulas opcionales de título y guardar). | **[VALIDO]** Árbol sintáctico generado sin errores. |
| `ejemplos/validos/04_operaciones_corte2.coco` | Operaciones del Corte 2: `eliminar_duplicados`, `eliminar_nulos`, `rellenar_nulos`, `convertir`, `crear`, `ordenar`, `renombrar`, `agrupar`, `resumir` y `guardar ... como`. | **[VALIDO]** Árbol sintáctico generado sin errores. |

**Total positivos:** 4/4 archivos aprobados exitosamente.

---

### 2. Pruebas Negativas (Detección de Errores)

| Archivo | Error inducido | Diagnóstico reportado |
|---|---|---|
| `ejemplos/invalidos/01_error_lexico_cadena_sin_cerrar.coco` | Falta comilla de cierre en ruta de CSV. | **[INVALIDO]** `linea 2, columna 16: token recognition error at: '"datos/ventas.csv;\n'` |
| `ejemplos/invalidos/02_error_sintactico_falta_punto_coma.coco` | Sentencia sin terminador `;`. | **[INVALIDO]** `linea 4, columna 0: missing ';' at 'resumen'` |
| `ejemplos/invalidos/03_error_palabra_reservada_como_identificador.coco` | Uso de `x` (palabra reservada) como nombre de variable. | **[INVALIDO]** `linea 3, columna 0: mismatched input 'x' expecting {'graficar', 'guardar', ID}` |

**Total negativos:** 3/3 archivos rechazados correctamente con posición exacta de línea y columna.

---

## Pruebas de Unidad del Motor de Datos (`Tabla` en Python puro)

Mediante `python3 test_tabla.py`:
- **Carga de CSV:** 15 registros cargados desde `datos/ventas.csv` con inferencia automática de tipos (`int`, `float`, `str`).
- **Filtrado:** `unidades > 5 && precio >= 1000` redujo correctamente el dataset a 6 filas.
- **Columna calculada:** `total = unidades * precio` calculada fila por fila.
- **Ordenamiento:** Ordenamiento descendente por `total` verificado.
- **Agrupamiento y agregaciones:** `agrupar por [ciudad]` + `resumir` calculó correctamente suma, media, mediana, máximo y desviación estándar muestral.
- **Exportación:** Generación y re-lectura exitosa de `salidas/resumen_ciudades_test.csv`.
