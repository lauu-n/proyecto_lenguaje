# Reporte de pruebas — corte 1

## Alcance

Se valida el front-end, sin ejecutar datos, variables ni gráficas.
La suite usa `unittest` de la biblioteca estándar y el runtime ANTLR
4.13.2 fijado en `requirements.txt`.

```text
python -m unittest discover -s tests -v
```

## Resultado observado

**83 tests aprobados**, sin fallos ni errores, en Windows con Python 3.12
y `antlr4-python3-runtime` 4.13.2. El test de ejemplos contiene seis
subcasos: los tres positivos se aceptan y los tres negativos se rechazan.
ANTLR 4.13.2 sobre Java 17 regeneró el lexer/parser sin diagnósticos.
No se afirma haber ejecutado la suite en Linux/macOS o en todas las
versiones de Python; esas instrucciones usan las mismas entradas
portables, pero requieren verificación en el entorno de destino.

## Cobertura y regresiones

| Grupo | Comprobaciones |
|---|---|
| Ejemplos originales | Resultado esperado para las seis fuentes del repositorio. |
| Reconocimiento | Asignaciones, carga, selección, filtros encadenados, 14 operadores y cinco tipos de gráfica. |
| Restricciones | Programa no vacío, terminador, listas no vacías, palabras reservadas, ASCII y formatos numéricos. |
| Cadenas | Unicode, cadena vacía, escapes de comilla/barra, escapes desconocidos y cierre/saltos de línea inválidos. |
| Estructura | Unario antes de potencia, potencia derecha, resta izquierda, multiplicación antes de suma, AND antes de OR y paréntesis. |
| Tokens | Prioridad de palabra reservada frente a ID, enteros, decimales, booleanos y descarte de comentarios. |
| Diagnósticos | Etapa léxica/sintáctica, coordenadas desde 1 y explicación de punto y coma ausente. |
| Consola | Estados 0/1/2, lotes mixtos, rutas inexistentes, patrones, UTF-8 inválido/BOM, ejecución como módulo y árbol completo. |
| Alcance de fase | Variables no declaradas y filtros no booleanos se reconocen sintácticamente; su validación queda para el corte 2. |

La suite falla si el resultado observado difiere de la expectativa. Los
negativos no se ejecutan como una lista de comandos cuyo fallo se ignore.
Las comprobaciones de precedencia inspeccionan el árbol; no evalúan
resultados numéricos ni implementan un Visitor semántico.

## Cambios verificados respecto a la revisión inicial

- EBNF alineada con programa no vacío y unarios con prioridad sobre `^`.
- Escape de barra/comilla explícito: la barra no puede consumirse como
  carácter ordinario para ocultar una comilla de cierre ausente.
- Artefactos ANTLR incluidos, con regeneración documentada.
- Fuentes inválidas devuelven estado 1; errores de lectura no cancelan el lote.
- Diagnósticos con etapa, posición y fragmento; árbol completo opcional.
- Pruebas positivas/negativas y estructurales automatizadas.

Las pruebas aportan evidencia reproducible; no garantizan ausencia de
todo defecto posible ni evalúan los requisitos de los cortes 2 y 3.
