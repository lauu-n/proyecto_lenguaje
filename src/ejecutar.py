"""Intérprete y Evaluador del Lenguaje Cocosette (Patrón Visitor).

Este módulo recorre el árbol de sintaxis abstracta (AST) generado por ANTLR
y ejecuta paso a paso cada instrucción del lenguaje Cocosette.

Estructura del archivo:
Está organizado de abajo hacia arriba (de lo más básico a lo más complejo).
Cada función o método se declara antes de cualquier otro bloque que lo llame,
garantizando un orden lógico, limpio y fácil de entender y sustentar.
"""

import sys
from pathlib import Path
from typing import Any, List, Optional

from antlr4 import CommonTokenStream, InputStream

# Configurar rutas para encontrar los módulos del proyecto y de ANTLR
directorio_actual = Path(__file__).resolve().parent
sys.path.append(str(directorio_actual / "parser"))
sys.path.append(str(directorio_actual))

from CocosetteLexer import CocosetteLexer
from CocosetteParser import CocosetteParser
from CocosetteVisitor import CocosetteVisitor
from memoria_ejecucion import MemoriaEjecucion
from tabla import AgrupacionTabla, Tabla


# ====================================================================
# 1. FUNCIONES AUXILIARES ELEMENTALES (NIVEL BÁSICO)
# ====================================================================
# Estas funciones se encargan de tareas simples de conversión de texto.
# No dependen de ninguna otra función personalizada.


def quitar_comillas(texto_con_comillas: str) -> str:
    """Quita las comillas dobles al inicio y al final de un texto si las tiene."""
    if len(texto_con_comillas) >= 2 and texto_con_comillas.startswith('"') and texto_con_comillas.endswith('"'):
        # Quitar la comilla inicial y la final
        texto_limpio = texto_con_comillas[1:-1]
        # Resolver caracteres de escape comunes
        texto_limpio = texto_limpio.replace('\\"', '"').replace('\\\\', '\\')
        return texto_limpio
    return texto_con_comillas


def convertir_texto_a_valor_literal(texto_crudo: str) -> Any:
    """Convierte el texto directo de un token en su valor real de Python.

    Ejemplos:
    - 'verdadero' -> True
    - 'falso'     -> False
    - '"hola"'    -> 'hola'
    - '42'        -> 42 (entero)
    - '3.14'      -> 3.14 (decimal)
    """
    texto_minuscula = texto_crudo.lower()

    # Caso 1: Valores booleanos
    if texto_minuscula == "verdadero":
        return True
    elif texto_minuscula == "falso":
        return False

    # Caso 2: Cadenas de texto entre comillas
    if texto_crudo.startswith('"'):
        return quitar_comillas(texto_crudo)

    # Caso 3: Número entero
    try:
        return int(texto_crudo)
    except ValueError:
        pass

    # Caso 4: Número decimal
    try:
        return float(texto_crudo)
    except ValueError:
        pass

    # Caso 5: Devolver el texto tal cual si no coincide con los anteriores
    return texto_crudo


# ====================================================================
# 2. CLASE DEL INTÉRPRETE VISITOR
# ====================================================================
# Hereda de CocosetteVisitor. Sus métodos están ordenados desde los más
# simples (literales y expresiones) hasta los más avanzados (tablas y programas).


class InterpreteCocosette(CocosetteVisitor):
    """Recorre el árbol de ANTLR y ejecuta las instrucciones del programa."""

    def __init__(self, memoria: Optional[MemoriaEjecucion] = None):
        super().__init__()
        # Memoria donde guardamos las variables del usuario (ej: ventas = ...)
        self.memoria: MemoriaEjecucion = memoria or MemoriaEjecucion()

        # Guarda la fila que se está procesando actualmente al evaluar expresiones
        self.fila_actual: Optional[dict] = None

        # Guarda la tabla sobre la cual está trabajando el pipeline activo (|>)
        self.tabla_en_proceso: Optional[Any] = None

    # ----------------------------------------------------------------
    # A. LITERALES E IDENTIFICADORES (ELEMENTALES)
    # ----------------------------------------------------------------

    def visitLiteral(self, ctx: CocosetteParser.LiteralContext):
        """Devuelve el valor en Python de un dato literal (número, texto o booleano)."""
        texto_literal = ctx.getText()
        return convertir_texto_a_valor_literal(texto_literal)

    def visitExpLiteral(self, ctx: CocosetteParser.ExpLiteralContext):
        """Evalúa un literal dentro de una expresión matemática o lógica."""
        return self.visitLiteral(ctx.literal())

    def visitExpIdentificador(self, ctx: CocosetteParser.ExpIdentificadorContext):
        """Busca el valor de un nombre (puede ser una columna o una variable)."""
        nombre = ctx.ID().getText()

        # 1. Si estamos recorriendo filas de una tabla, buscamos primero si es una columna
        if self.fila_actual is not None and nombre in self.fila_actual:
            return self.fila_actual[nombre]

        # 2. Si no es una columna de la fila actual, lo buscamos en la memoria general
        linea = ctx.start.line
        columna = ctx.start.column
        return self.memoria.obtener(nombre, linea=linea, columna=columna)

    # ----------------------------------------------------------------
    # B. OPERACIONES MATEMÁTICAS Y LÓGICAS (ORDEN DE PRECEDENCIA)
    # ----------------------------------------------------------------

    def visitExpParentesis(self, ctx: CocosetteParser.ExpParentesisContext):
        """Evalúa una expresión encerrada entre paréntesis (expresion)."""
        return self.visit(ctx.expresion())

    def visitExpUnaria(self, ctx: CocosetteParser.ExpUnariaContext):
        """Evalúa operadores unarios: negativo (-x) o negación lógica (!x)."""
        operador = ctx.op.text
        valor = self.visit(ctx.expresion())

        if operador == "-":
            if valor is None:
                return None
            return -valor
        elif operador == "!":
            return not bool(valor)

        return valor

    def visitExpPotencia(self, ctx: CocosetteParser.ExpPotenciaContext):
        """Calcula la potencia entre dos números: base ^ exponente."""
        base = self.visit(ctx.expresion(0))
        exponente = self.visit(ctx.expresion(1))

        if base is None or exponente is None:
            return None

        return base ** exponente

    def visitExpMultiplicativa(self, ctx: CocosetteParser.ExpMultiplicativaContext):
        """Calcula multiplicación (*), división (/) o residuo (%)."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

        # Si algún valor es nulo, el resultado del cálculo es nulo
        if lado_izquierdo is None or lado_derecho is None:
            return None

        if operador == "*":
            return lado_izquierdo * lado_derecho

        elif operador == "/":
            # Validar división por cero
            if lado_derecho == 0:
                linea = ctx.start.line
                columna = ctx.start.column
                raise ZeroDivisionError(
                    f"Error semántico (línea {linea}, columna {columna}): división por cero."
                )
            return lado_izquierdo / lado_derecho

        elif operador == "%":
            # Validar residuo por cero
            if lado_derecho == 0:
                linea = ctx.start.line
                columna = ctx.start.column
                raise ZeroDivisionError(
                    f"Error semántico (línea {linea}, columna {columna}): residuo por cero."
                )
            return lado_izquierdo % lado_derecho

        return None

    def visitExpAditiva(self, ctx: CocosetteParser.ExpAditivaContext):
        """Calcula suma (+) o resta (-). Si hay texto, la suma concatena."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

        if operador == "+":
            # Si alguno de los dos operandos es texto, hacemos concatenación
            if isinstance(lado_izquierdo, str) or isinstance(lado_derecho, str):
                texto_izq = "" if lado_izquierdo is None else str(lado_izquierdo)
                texto_der = "" if lado_derecho is None else str(lado_derecho)
                return texto_izq + texto_der

            # Si son números y alguno es nulo, da nulo
            if lado_izquierdo is None or lado_derecho is None:
                return None

            return lado_izquierdo + lado_derecho

        elif operador == "-":
            if lado_izquierdo is None or lado_derecho is None:
                return None

            return lado_izquierdo - lado_derecho

        return None

    def visitExpRelacional(self, ctx: CocosetteParser.ExpRelacionalContext):
        """Compara magnitudes: menor (<), menor o igual (<=), mayor (>), mayor o igual (>=)."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

        # Si falta algún valor, la comparación no se cumple
        if lado_izquierdo is None or lado_derecho is None:
            return False

        if operador == "<":
            return lado_izquierdo < lado_derecho
        elif operador == "<=":
            return lado_izquierdo <= lado_derecho
        elif operador == ">":
            return lado_izquierdo > lado_derecho
        elif operador == ">=":
            return lado_izquierdo >= lado_derecho

        return False

    def visitExpIgualdad(self, ctx: CocosetteParser.ExpIgualdadContext):
        """Compara si dos valores son iguales (==) o diferentes (!=)."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

        if operador == "==":
            return lado_izquierdo == lado_derecho
        elif operador == "!=":
            return lado_izquierdo != lado_derecho

        return False

    def visitExpAnd(self, ctx: CocosetteParser.ExpAndContext):
        """Evalúa la conjunción lógica (&&)."""
        lado_izquierdo = bool(self.visit(ctx.expresion(0)))
        # Si la izquierda ya es falsa, no hace falta evaluar la derecha
        if not lado_izquierdo:
            return False

        lado_derecho = bool(self.visit(ctx.expresion(1)))
        return lado_izquierdo and lado_derecho

    def visitExpOr(self, ctx: CocosetteParser.ExpOrContext):
        """Evalúa la disyunción lógica (||)."""
        lado_izquierdo = bool(self.visit(ctx.expresion(0)))
        # Si la izquierda ya es verdadera, no hace falta evaluar la derecha
        if lado_izquierdo:
            return True

        lado_derecho = bool(self.visit(ctx.expresion(1)))
        return lado_izquierdo or lado_derecho

    # ----------------------------------------------------------------
    # C. PARÁMETROS AUXILIARES DE TABLAS Y CONDICIONES
    # ----------------------------------------------------------------

    def visitCocondicion(self, ctx: CocosetteParser.CocondicionContext):
        """Evalúa la condición de un filtro."""
        return self.visit(ctx.expresion())

    def visitListaCocolumnas(self, ctx: CocosetteParser.ListaCocolumnasContext) -> List[str]:
        """Extrae la lista de nombres de columnas escritas por el usuario."""
        nombres = []
        for nodo_id in ctx.ID():
            nombres.append(nodo_id.getText())
        return nombres

    def visitTipoDato(self, ctx: CocosetteParser.TipoDatoContext) -> str:
        """Devuelve el tipo de dato destino como texto ('entero', 'decimal', etc.)."""
        return ctx.getText().lower()

    def visitFuncionAgregacion(self, ctx: CocosetteParser.FuncionAgregacionContext) -> str:
        """Devuelve el nombre de la función agregadora ('suma', 'media', etc.)."""
        return ctx.getText().lower()

    def visitAsignacionAgregada(self, ctx: CocosetteParser.AsignacionAgregadaContext):
        """Devuelve los datos de una agregación: (nombre_salida, función, columna_origen)."""
        nombre_salida = ctx.ID(0).getText()
        funcion = self.visitFuncionAgregacion(ctx.funcionAgregacion())

        # La columna de entrada es opcional (por ejemplo contar() no necesita columna)
        columna_origen = None
        if len(ctx.ID()) > 1:
            columna_origen = ctx.ID(1).getText()

        return (nombre_salida, funcion, columna_origen)

    # ----------------------------------------------------------------
    # D. OPERACIONES DE PIPELINE SOBRE TABLAS
    # ----------------------------------------------------------------
    # Cada una de estas operaciones recibe los datos de `self.tabla_en_proceso`
    # y retorna una nueva tabla transformada.

    def visitCocoSeleccion(self, ctx: CocosetteParser.CocoSeleccionContext) -> Tabla:
        """Filtra y deja únicamente las columnas seleccionadas."""
        columnas_deseadas = self.visitListaCocolumnas(ctx.listaCocolumnas())
        return self.tabla_en_proceso.seleccionar(columnas_deseadas)

    def visitCocoFiltro(self, ctx: CocosetteParser.CocoFiltroContext) -> Tabla:
        """Filtra las filas de la tabla según una condición booleana."""
        def evaluar_fila(fila: dict) -> bool:
            # Ponemos temporalmente la fila actual en el intérprete
            self.fila_actual = fila
            cumple_condicion = bool(self.visitCocondicion(ctx.cocondicion()))
            self.fila_actual = None
            return cumple_condicion

        return self.tabla_en_proceso.filtrar(evaluar_fila)

    def visitCocoCrear(self, ctx: CocosetteParser.CocoCrearContext) -> Tabla:
        """Crea una nueva columna calculando una expresión para cada fila."""
        nombre_nueva_columna = ctx.ID().getText()

        def calcular_valor_para_fila(fila: dict) -> Any:
            self.fila_actual = fila
            valor_calculado = self.visit(ctx.expresion())
            self.fila_actual = None
            return valor_calculado

        return self.tabla_en_proceso.crear_columna(nombre_nueva_columna, calcular_valor_para_fila)

    def visitCocoOrdenar(self, ctx: CocosetteParser.CocoOrdenarContext) -> Tabla:
        """Ordena las filas según una columna de forma ascendente o descendente."""
        columna = ctx.ID().getText()
        es_ascendente = True

        # Revisar si el usuario especificó descendente
        if ctx.COCODESC() is not None:
            es_ascendente = False
        elif ctx.COCOASC() is not None:
            es_ascendente = True

        return self.tabla_en_proceso.ordenar(columna, ascendente=es_ascendente)

    def visitCocoRenombrar(self, ctx: CocosetteParser.CocoRenombrarContext) -> Tabla:
        """Cambia el nombre de una columna existente por uno nuevo."""
        columna_actual = ctx.ID(0).getText()
        columna_nueva = ctx.ID(1).getText()
        return self.tabla_en_proceso.renombrar(columna_actual, columna_nueva)

    def visitCocoEliminarDuplicados(self, ctx: CocosetteParser.CocoEliminarDuplicadosContext) -> Tabla:
        """Elimina las filas exactamente repetidas conservando la primera."""
        return self.tabla_en_proceso.eliminar_duplicados()

    def visitCocoTratarNulos(self, ctx: CocosetteParser.CocoTratarNulosContext) -> Tabla:
        """Elimina filas con nulos o rellena los nulos de una columna con un valor."""
        # Opción 1: eliminar_nulos
        if ctx.COCOELIMINARNULL() is not None:
            return self.tabla_en_proceso.eliminar_nulos()

        # Opción 2: rellenar_nulos columna con valor
        columna = ctx.ID().getText()
        valor_reemplazo = self.visit(ctx.expresion())
        return self.tabla_en_proceso.rellenar_nulos(columna, valor_reemplazo)

    def visitCocoConvertir(self, ctx: CocosetteParser.CocoConvertirContext) -> Tabla:
        """Convierte los tipos de datos de una columna (entero, decimal, texto, booleano)."""
        columna = ctx.ID().getText()
        tipo_destino = self.visitTipoDato(ctx.tipoDato())
        return self.tabla_en_proceso.convertir(columna, tipo_destino)

    def visitCocoAgrupar(self, ctx: CocosetteParser.CocoAgruparContext) -> AgrupacionTabla:
        """Agrupa las filas por una o más columnas para poder calcular estadísticas."""
        columnas_agrupadoras = self.visitListaCocolumnas(ctx.listaCocolumnas())
        return self.tabla_en_proceso.agrupar_por(columnas_agrupadoras)

    def visitCocoResumir(self, ctx: CocosetteParser.CocoResumirContext) -> Tabla:
        """Aplica funciones de agregación (suma, media, contar, etc.) sobre los grupos."""
        lista_especificaciones = []
        for nodo_asig in ctx.asignacionAgregada():
            especificacion = self.visitAsignacionAgregada(nodo_asig)
            lista_especificaciones.append(especificacion)

        # Si la tabla ya estaba agrupada, calculamos directamente sobre sus grupos
        if isinstance(self.tabla_en_proceso, AgrupacionTabla):
            return self.tabla_en_proceso.resumir(lista_especificaciones)

        # Si no estaba agrupada, agrupamos por lista vacía (resumen de toda la tabla)
        agrupacion_global = AgrupacionTabla(self.tabla_en_proceso, [])
        return agrupacion_global.resumir(lista_especificaciones)

    def visitCocoGraficar(self, ctx: CocosetteParser.CocoGraficarContext):
        """Notificación de gráfico (diseñado para la entrega de Corte 3)."""
        tipo = ctx.cocoGrafica().getText()
        tabla_nombre = ctx.ID(0).getText()
        eje_x = ctx.ID(1).getText()
        eje_y = ctx.ID(2).getText()
        print(f"[Grafica] Generando gráfico de '{tipo}' sobre '{tabla_nombre}' (eje x: {eje_x}, eje y: {eje_y}).")
        return None

    def visitOperacion(self, ctx: CocosetteParser.OperacionContext):
        """Identifica cuál operación de pipeline se llamó y la ejecuta."""
        if ctx.cocoSeleccion() is not None:
            return self.visitCocoSeleccion(ctx.cocoSeleccion())
        elif ctx.cocoFiltro() is not None:
            return self.visitCocoFiltro(ctx.cocoFiltro())
        elif ctx.cocoCrear() is not None:
            return self.visitCocoCrear(ctx.cocoCrear())
        elif ctx.cocoOrdenar() is not None:
            return self.visitCocoOrdenar(ctx.cocoOrdenar())
        elif ctx.cocoRenombrar() is not None:
            return self.visitCocoRenombrar(ctx.cocoRenombrar())
        elif ctx.cocoEliminarDuplicados() is not None:
            return self.visitCocoEliminarDuplicados(ctx.cocoEliminarDuplicados())
        elif ctx.cocoTratarNulos() is not None:
            return self.visitCocoTratarNulos(ctx.cocoTratarNulos())
        elif ctx.cocoConvertir() is not None:
            return self.visitCocoConvertir(ctx.cocoConvertir())
        elif ctx.cocoAgrupar() is not None:
            return self.visitCocoAgrupar(ctx.cocoAgrupar())
        elif ctx.cocoResumir() is not None:
            return self.visitCocoResumir(ctx.cocoResumir())

        raise NotImplementedError("Operación de pipeline no reconocida en la gramática.")

    # ----------------------------------------------------------------
    # E. CARGA, GUARDADO, FUENTES DE DATOS Y PIPELINES
    # ----------------------------------------------------------------

    def visitCargaCSV(self, ctx: CocosetteParser.CargaCSVContext) -> Tabla:
        """Carga un archivo CSV desde el disco duro y crea una Tabla."""
        ruta_archivo = quitar_comillas(ctx.STRING().getText())
        return Tabla.cargar_csv(ruta_archivo)

    def visitCocoGuardarCSV(self, ctx: CocosetteParser.CocoGuardarCSVContext):
        """Exporta una tabla almacenada en memoria a un archivo CSV."""
        nombre_variable = ctx.ID().getText()
        ruta_destino = quitar_comillas(ctx.STRING().getText())

        linea = ctx.start.line
        columna = ctx.start.column
        tabla_a_guardar = self.memoria.obtener(nombre_variable, linea=linea, columna=columna)

        if not isinstance(tabla_a_guardar, Tabla):
            raise TypeError(
                f"Error semántico (línea {linea}, columna {columna}): "
                f"la variable '{nombre_variable}' no es una tabla y no se puede guardar como CSV."
            )

        tabla_a_guardar.guardar_csv(ruta_destino)
        print(f"[Exportación] Tabla '{nombre_variable}' guardada exitosamente en: '{ruta_destino}'")
        return None

    def visitFuenteCarga(self, ctx: CocosetteParser.FuenteCargaContext):
        """Procesa una fuente que proviene de cargar un archivo CSV."""
        return self.visitCargaCSV(ctx.cargaCSV())

    def visitFuenteExpresion(self, ctx: CocosetteParser.FuenteExpresionContext):
        """Procesa una fuente que es una expresión matemática o lógica simple."""
        return self.visit(ctx.expresion())

    def visitFuentePipeline(self, ctx: CocosetteParser.FuentePipelineContext) -> Tabla:
        """Ejecuta una cadena de transformaciones paso a paso: datos |> op1 |> op2."""
        nombre_tabla_origen = ctx.ID().getText()
        linea = ctx.start.line
        columna = ctx.start.column

        # 1. Obtener la tabla original desde la memoria
        resultado_actual = self.memoria.obtener(nombre_tabla_origen, linea=linea, columna=columna)

        # 2. Aplicar cada operación encadenada con |>
        for nodo_operacion in ctx.operacion():
            self.tabla_en_proceso = resultado_actual
            resultado_actual = self.visitOperacion(nodo_operacion)

        # Limpiar la referencia de la tabla en proceso
        self.tabla_en_proceso = None
        return resultado_actual

    # ----------------------------------------------------------------
    # F. ASIGNACIONES, SENTENCIAS Y PROGRAMA COMPLETO
    # ----------------------------------------------------------------

    def visitAsignacion(self, ctx: CocosetteParser.AsignacionContext):
        """Ejecuta una asignación del estilo: variable = fuente."""
        nombre_variable = ctx.ID().getText()
        valor_calculado = self.visit(ctx.cocoFuente())

        # Guardar en la memoria de variables
        self.memoria.guardar(nombre_variable, valor_calculado)

        # Mostrar retroalimentación clara en la consola
        if isinstance(valor_calculado, Tabla):
            print(f"[Asignación] '{nombre_variable}' -> Tabla ({len(valor_calculado.filas)} filas, columnas: {valor_calculado.columnas})")
        else:
            print(f"[Asignación] '{nombre_variable}' = {valor_calculado}")

        return valor_calculado

    def visitSentencia(self, ctx: CocosetteParser.SentenciaContext):
        """Ejecuta una única sentencia (asignación, guardado o gráfico)."""
        if ctx.asignacion() is not None:
            return self.visitAsignacion(ctx.asignacion())
        elif ctx.cocoGuardarCSV() is not None:
            return self.visitCocoGuardarCSV(ctx.cocoGuardarCSV())
        elif ctx.cocoGraficar() is not None:
            return self.visitCocoGraficar(ctx.cocoGraficar())
        return None

    def visitPrograma(self, ctx: CocosetteParser.ProgramaContext) -> MemoriaEjecucion:
        """Ejecuta todas las sentencias del programa en orden secuencial."""
        for nodo_sentencia in ctx.sentencia():
            self.visitSentencia(nodo_sentencia)
        return self.memoria


# ====================================================================
# 3. FUNCIONES DE EJECUCIÓN EXTERNA (PUNTO DE ENTRADA / NIVEL ALTO)
# ====================================================================
# Estas funciones orquestan todo el proceso: leen el código fuente,
# llaman al lexer, al parser y finalmente al intérprete.


def ejecutar_codigo(codigo_fuente: str, memoria: Optional[MemoriaEjecucion] = None) -> MemoriaEjecucion:
    """Toma una cadena de texto con código Cocosette y la ejecuta completamente."""
    # 1. Crear el flujo de caracteres para ANTLR
    flujo_entrada = InputStream(codigo_fuente)

    # 2. Fase de análisis léxico (crear tokens)
    lexer = CocosetteLexer(flujo_entrada)
    flujo_tokens = CommonTokenStream(lexer)

    # 3. Fase de análisis sintáctico (construir el árbol AST)
    parser = CocosetteParser(flujo_tokens)
    arbol = parser.programa()

    # 4. Fase de ejecución semántica (Visitor)
    interprete = InterpreteCocosette(memoria=memoria)
    interprete.visitPrograma(arbol)

    return interprete.memoria


def ejecutar_archivo(ruta_archivo: str, memoria: Optional[MemoriaEjecucion] = None) -> MemoriaEjecucion:
    """Lee un archivo .coco desde el disco duro y lo ejecuta."""
    ruta = Path(ruta_archivo)
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de programa: '{ruta_archivo}'")

    print(f"\n========================================================")
    print(f"  Ejecutando Cocosette: {ruta.name}")
    print(f"========================================================")

    contenido = ruta.read_text(encoding="utf-8")
    return ejecutar_codigo(contenido, memoria=memoria)


def main():
    """Punto de entrada de línea de comandos: python ejecutar.py archivo.coco"""
    if len(sys.argv) < 2:
        print("Uso del intérprete Cocosette:")
        print("  python src/ejecutar.py <archivo.coco>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]
    try:
        memoria_final = ejecutar_archivo(ruta_archivo)
        print("\n[Éxito] Ejecución finalizada correctamente.")
        print(memoria_final)
    except Exception as error:
        print(f"\n[ERROR DURANTE LA EJECUCIÓN]: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
