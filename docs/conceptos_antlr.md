# Conceptos clave de ANTLR usados en Cocosette

Esta guía explica los fundamentos de ANTLR4 utilizados en el proyecto: qué genera el comando `antlr4`, de qué clases base hereda cada componente y cómo se articulan el parser, el visitor y el motor de ejecución.

---

## 1. Lexer vs. Parser

- **Lexer (Analizador léxico):** Convierte el texto fuente `.coco` carácter por carácter en una secuencia de **tokens** (`COCOCARGAR`, `ID`, `STRING`, `';'`, etc.).
- **Parser (Analizador sintáctico):** Toma los tokens generados por el lexer y comprueba que sigan las reglas gramaticales del lenguaje (orden de sentencias, jerarquía de expresiones, etc.), construyendo el **árbol de análisis sintáctico** (*Parse Tree*).

En `grammar/Cocosette.g4`:
- Reglas en **MAYÚSCULAS** (`COCOCARGAR`, `ID`, `STRING`, `INT`): son reglas del **Lexer**.
- Reglas en **minúsculas** (`programa`, `sentencia`, `cocoFuente`, `expresion`): son reglas del **Parser**.

---

## 2. Artefactos generados por ANTLR y Jerarquía de Herencia

Al ejecutar `make generar` (que corre internamente `antlr4 -Dlanguage=Python3 -visitor -o ../src/parser Cocosette.g4` desde `grammar/`), ANTLR produce los siguientes archivos en `src/parser/`:

| Archivo generado | Clase Python | Hereda de | Propósito |
|---|---|---|---|
| `CocosetteLexer.py` | `CocosetteLexer` | `Lexer` (`antlr4`) | Tokenizador específico del DSL Cocosette. |
| `CocosetteParser.py` | `CocosetteParser` | `Parser` (`antlr4`) | Reconocedor de gramática y constructor del árbol. |
| `CocosetteVisitor.py` | `CocosetteVisitor` | `ParseTreeVisitor` (`antlr4`) | Interfaz para recorrer y evaluar el árbol (patrón Visitor). |
| `CocosetteListener.py` | `CocosetteListener` | `ParseTreeListener` (`antlr4`) | Interfaz basada en eventos al entrar/salir de nodos. |

### Arquitectura de capas:

```
Capa 1: Runtime de ANTLR (antlr4-python3-runtime)
        Lexer, Parser, ParseTreeVisitor, ErrorListener, FileStream, CommonTokenStream
           ▲
           │ (Herencia)
           │
Capa 2: Código generado por ANTLR (src/parser/)
        CocosetteLexer, CocosetteParser, CocosetteVisitor
           ▲
           │ (Uso e invocación)
           │
Capa 3: Código propio del proyecto (src/)
        validar.py, tabla.py, memoria_ejecucion.py
```

---

## 3. Recorrido de Ejecución en `src/validar.py`

Cuando se ejecuta `python3 src/validar.py archivo.coco`:

1. `FileStream("archivo.coco", encoding="utf-8")` lee el archivo de texto.
2. `CocosetteLexer` tokeniza el flujo de entrada.
3. Se desasocian los listeners de consola por defecto y se conecta `ColectorDeErrores(ErrorListener)` para interceptar errores léxicos.
4. `CommonTokenStream` almacena y suministra tokens bajo demanda al parser.
5. `CocosetteParser` ejecuta la regla raíz `programa()`, construyendo el árbol sintáctico `ProgramaContext`.
6. Si ocurrieron errores léxicos o sintácticos, se imprime `[INVALIDO]` con línea y columna. De lo contrario, se imprime `[VALIDO]` junto con la representación en texto del árbol.

---

## 4. Alternativas Etiquetadas y el Patrón Visitor (Corte 2)

En `grammar/Cocosette.g4`, reglas como `cocoFuente` utilizan etiquetas (`# nombre`):

```antlr
cocoFuente
    : cargaCSV                     # fuenteCarga
    | ID ( PIPE operacion )+       # fuentePipeline
    | expresion                    # fuenteExpresion
    ;
```

ANTLR genera una clase de contexto para cada alternativa (`FuenteCargaContext`, `FuentePipelineContext`, `FuenteExpresionContext`). En el Visitor de ejecución del Corte 2, cada una corresponde a un método (`visitFuenteCarga`, `visitFuentePipeline`, etc.), permitiendo que el intérprete ejecute la acción correcta de forma limpia y polimórfica.
