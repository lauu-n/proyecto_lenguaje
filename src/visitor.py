"""Visitor e Interprete para el lenguaje Cocosette.

Este modulo hereda de la clase CocosetteVisitor generada por ANTLR
y le da vida al lenguaje, ejecutando las operaciones matematicas,
logicas y de manipulacion de datos tabulares (Corte II).

Estructura:
Organizado estrictamente de abajo hacia arriba (de lo mas elemental
a lo mas complejo). Cada funcion se declara antes de cualquier otra
que la llame.
"""

import sys

# Agregar carpetas de modulos al path de Python
sys.path.append("src/parser")
sys.path.append("src")
sys.path.append("parser")

from CocosetteVisitor import CocosetteVisitor
from memoria_ejecucion import MemoriaEjecucion
from tabla import AgrupacionTabla, Tabla


# ====================================================================
# 1. FUNCIONES AUXILIARES ELEMENTALES (NIVEL BASICO)
# ====================================================================


def quitar_comillas(texto_con_comillas):
    """Quita las comillas dobles al inicio y al final de una cadena de texto."""
    if len(texto_con_comillas) >= 2 and texto_con_comillas.startswith('"') and texto_con_comillas.endswith('"'):
        texto_limpio = texto_con_comillas[1:-1]
        texto_limpio = texto_limpio.replace('\\"', '"').replace('\\\\', '\\')
        return texto_limpio
    return texto_con_comillas


def convertir_texto_a_valor_literal(texto_crudo):
    """Convierte el texto directo de un token en su valor real en Python.

    Ejemplos:
    - 'verdadero' -> True
    - 'falso'     -> False
    - '"hola"'    -> 'hola'
    - '42'        -> 42 (entero)
    - '3.14'      -> 3.14 (decimal)
    """
    texto_minuscula = texto_crudo.lower()

    if texto_minuscula == "verdadero":
        return True
    elif texto_minuscula == "falso":
        return False

    if texto_crudo.startswith('"'):
        return quitar_comillas(texto_crudo)

    try:
        return int(texto_crudo)
    except ValueError:
        pass

    try:
        return float(texto_crudo)
    except ValueError:
        pass

    return texto_crudo


# ====================================================================
# 2. CLASE INTERPRETE VISITOR (HEREDA DE COCOSSETTEVISITOR)
# ====================================================================


class InterpreteVisitor(CocosetteVisitor):
    """Recorre el arbol sintactico y ejecuta las instrucciones del lenguaje."""

    def __init__(self, memoria=None):
        super().__init__()
        # Memoria donde guardamos las variables creadas por el usuario
        if memoria is not None:
            self.memoria = memoria
        else:
            self.memoria = MemoriaEjecucion()

        # Fila que se esta evaluando actualmente (para saber el valor de las columnas)
        self.fila_actual = None

        # Tabla sobre la cual esta operando el pipeline activo (|>)
        self.tabla_en_proceso = None

    # ----------------------------------------------------------------
    # A. LITERALES E IDENTIFICADORES (LO MAS BASICO)
    # ----------------------------------------------------------------

    def visitLiteral(self, ctx):
        """Devuelve el valor en Python de un dato literal (numero, texto, booleano)."""
        texto_literal = ctx.getText()
        return convertir_texto_a_valor_literal(texto_literal)

    def visitExpLiteral(self, ctx):
        """Evalua un literal dentro de una expresion matematica o logica."""
        return self.visitLiteral(ctx.literal())

    def visitExpIdentificador(self, ctx):
        """Busca el valor de un identificador (columna de fila o variable en memoria)."""
        nombre = ctx.ID().getText()

        # 1. Si estamos recorriendo filas de una tabla, buscamos primero en la fila
        if self.fila_actual is not None and nombre in self.fila_actual:
            return self.fila_actual[nombre]

        # 2. Si no es una columna de la fila actual, lo buscamos en la memoria general
        linea = ctx.start.line
        columna = ctx.start.column
        return self.memoria.obtener(nombre, linea=linea, columna=columna)

    # ----------------------------------------------------------------
    # B. OPERACIONES MATEMATICAS Y LOGICAS
    # ----------------------------------------------------------------

    def visitExpParentesis(self, ctx):
        """Evalua una expresion entre parentesis: (expresion)."""
        return self.visit(ctx.expresion())

    def visitExpUnaria(self, ctx):
        """Evalua negativo (-x) o negacion logica (!x)."""
        operador = ctx.op.text
        valor = self.visit(ctx.expresion())

        if operador == "-":
            if valor is None:
                return None
            return -valor
        elif operador == "!":
            return not bool(valor)

        return valor

    def visitExpPotencia(self, ctx):
        """Calcula potencia: base ^ exponente."""
        base = self.visit(ctx.expresion(0))
        exponente = self.visit(ctx.expresion(1))

        if base is None or exponente is None:
            return None

        return base ** exponente

    def visitExpMultiplicativa(self, ctx):
        """Calcula multiplicacion (*), division (/) o residuo (%)."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

        if lado_izquierdo is None or lado_derecho is None:
            return None

        if operador == "*":
            return lado_izquierdo * lado_derecho

        elif operador == "/":
            if lado_derecho == 0:
                linea = ctx.start.line
                columna = ctx.start.column
                raise ZeroDivisionError(
                    f"Error semantico (linea {linea}, columna {columna}): division por cero."
                )
            return lado_izquierdo / lado_derecho

        elif operador == "%":
            if lado_derecho == 0:
                linea = ctx.start.line
                columna = ctx.start.column
                raise ZeroDivisionError(
                    f"Error semantico (linea {linea}, columna {columna}): residuo por cero."
                )
            return lado_izquierdo % lado_derecho

        return None

    def visitExpAditiva(self, ctx):
        """Calcula suma (+) o resta (-). Si hay texto, la suma concatena."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

        if operador == "+":
            if isinstance(lado_izquierdo, str) or isinstance(lado_derecho, str):
                texto_izq = "" if lado_izquierdo is None else str(lado_izquierdo)
                texto_der = "" if lado_derecho is None else str(lado_derecho)
                return texto_izq + texto_der

            if lado_izquierdo is None or lado_derecho is None:
                return None

            return lado_izquierdo + lado_derecho

        elif operador == "-":
            if lado_izquierdo is None or lado_derecho is None:
                return None

            return lado_izquierdo - lado_derecho

        return None

    def visitExpRelacional(self, ctx):
        """Compara menor (<), menor o igual (<=), mayor (>), mayor o igual (>=)."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

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

    def visitExpIgualdad(self, ctx):
        """Compara si dos valores son iguales (==) o diferentes (!=)."""
        lado_izquierdo = self.visit(ctx.expresion(0))
        lado_derecho = self.visit(ctx.expresion(1))
        operador = ctx.op.text

        if operador == "==":
            return lado_izquierdo == lado_derecho
        elif operador == "!=":
            return lado_izquierdo != lado_derecho

        return False

    def visitExpAnd(self, ctx):
        """Evalua la conjuncion logica (&&)."""
        lado_izquierdo = bool(self.visit(ctx.expresion(0)))
        if not lado_izquierdo:
            return False

        lado_derecho = bool(self.visit(ctx.expresion(1)))
        return lado_izquierdo and lado_derecho

    def visitExpOr(self, ctx):
        """Evalua la disyuncion logica (||)."""
        lado_izquierdo = bool(self.visit(ctx.expresion(0)))
        if lado_izquierdo:
            return True

        lado_derecho = bool(self.visit(ctx.expresion(1)))
        return lado_izquierdo or lado_derecho

    # ----------------------------------------------------------------
    # C. PARAMETROS DE TABLA Y CONDICIONES
    # ----------------------------------------------------------------

    def visitCocondicion(self, ctx):
        """Evalua la condicion logica de un filtro."""
        return self.visit(ctx.expresion())

    def visitListaCocolumnas(self, ctx):
        """Devuelve la lista de nombres de columnas escritas por el usuario."""
        nombres = []
        for nodo_id in ctx.ID():
            nombres.append(nodo_id.getText())
        return nombres

    def visitTipoDato(self, ctx):
        """Devuelve el tipo de dato destino como texto ('entero', 'decimal', etc.)."""
        return ctx.getText().lower()

    def visitFuncionAgregacion(self, ctx):
        """Devuelve el nombre de la funcion agregadora ('suma', 'media', etc.)."""
        return ctx.getText().lower()

    def visitAsignacionAgregada(self, ctx):
        """Devuelve los datos de una agregacion: (nombre_salida, funcion, columna_origen)."""
        nombre_salida = ctx.ID(0).getText()
        funcion = self.visitFuncionAgregacion(ctx.funcionAgregacion())

        columna_origen = None
        if len(ctx.ID()) > 1:
            columna_origen = ctx.ID(1).getText()

        return (nombre_salida, funcion, columna_origen)

    # ----------------------------------------------------------------
    # D. OPERACIONES DE PIPELINE SOBRE TABLAS
    # ----------------------------------------------------------------

    def visitCocoSeleccion(self, ctx):
        """Deja unicamente las columnas seleccionadas en la tabla."""
        columnas_deseadas = self.visitListaCocolumnas(ctx.listaCocolumnas())
        return self.tabla_en_proceso.seleccionar(columnas_deseadas)

    def visitCocoFiltro(self, ctx):
        """Filtra las filas de la tabla segun una condicion."""
        def evaluar_fila(fila):
            self.fila_actual = fila
            cumple_condicion = bool(self.visitCocondicion(ctx.cocondicion()))
            self.fila_actual = None
            return cumple_condicion

        return self.tabla_en_proceso.filtrar(evaluar_fila)

    def visitCocoCrear(self, ctx):
        """Crea una nueva columna calculando una expresion para cada fila."""
        nombre_nueva_columna = ctx.ID().getText()

        def calcular_valor_para_fila(fila):
            self.fila_actual = fila
            valor_calculado = self.visit(ctx.expresion())
            self.fila_actual = None
            return valor_calculado

        return self.tabla_en_proceso.crear_columna(nombre_nueva_columna, calcular_valor_para_fila)

    def visitCocoOrdenar(self, ctx):
        """Ordena las filas segun una columna de forma ascendente o descendente."""
        columna = ctx.ID().getText()
        es_ascendente = True

        if ctx.COCODESC() is not None:
            es_ascendente = False
        elif ctx.COCOASC() is not None:
            es_ascendente = True

        return self.tabla_en_proceso.ordenar(columna, ascendente=es_ascendente)

    def visitCocoRenombrar(self, ctx):
        """Cambia el nombre de una columna existente por uno nuevo."""
        columna_actual = ctx.ID(0).getText()
        columna_nueva = ctx.ID(1).getText()
        return self.tabla_en_proceso.renombrar(columna_actual, columna_nueva)

    def visitCocoEliminarDuplicados(self, ctx):
        """Elimina las filas exactamente repetidas conservando la primera."""
        return self.tabla_en_proceso.eliminar_duplicados()

    def visitCocoTratarNulos(self, ctx):
        """Elimina filas con nulos o rellena los nulos con un valor dado."""
        if ctx.COCOELIMINARNULL() is not None:
            return self.tabla_en_proceso.eliminar_nulos()

        columna = ctx.ID().getText()
        valor_reemplazo = self.visit(ctx.expresion())
        return self.tabla_en_proceso.rellenar_nulos(columna, valor_reemplazo)

    def visitCocoConvertir(self, ctx):
        """Convierte los tipos de datos de una columna (entero, decimal, texto, booleano)."""
        columna = ctx.ID().getText()
        tipo_destino = self.visitTipoDato(ctx.tipoDato())
        return self.tabla_en_proceso.convertir(columna, tipo_destino)

    def visitCocoAgrupar(self, ctx):
        """Agrupa las filas por columnas para poder calcular agregaciones."""
        columnas_agrupadoras = self.visitListaCocolumnas(ctx.listaCocolumnas())
        return self.tabla_en_proceso.agrupar_por(columnas_agrupadoras)

    def visitCocoResumir(self, ctx):
        """Calcula funciones estadisticas (suma, media, contar, etc.) sobre los grupos."""
        lista_especificaciones = []
        for nodo_asig in ctx.asignacionAgregada():
            especificacion = self.visitAsignacionAgregada(nodo_asig)
            lista_especificaciones.append(especificacion)

        if isinstance(self.tabla_en_proceso, AgrupacionTabla):
            return self.tabla_en_proceso.resumir(lista_especificaciones)

        agrupacion_global = AgrupacionTabla(self.tabla_en_proceso, [])
        return agrupacion_global.resumir(lista_especificaciones)

    def visitCocoGraficar(self, ctx):
        """Notificacion informativa para graficas (correspondiente a Corte 3)."""
        tipo = ctx.cocoGrafica().getText()
        tabla_nombre = ctx.ID(0).getText()
        eje_x = ctx.ID(1).getText()
        eje_y = ctx.ID(2).getText()
        print(f"[Grafica] Grafico de tipo '{tipo}' sobre '{tabla_nombre}' (x: {eje_x}, y: {eje_y}).")
        return None

    def visitOperacion(self, ctx):
        """Identifica cual de las operaciones del pipeline se llamo y la ejecuta."""
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

        raise NotImplementedError("Operacion de pipeline no reconocida.")

    # ----------------------------------------------------------------
    # E. CARGA, GUARDADO, FUENTES DE DATOS Y PIPELINES
    # ----------------------------------------------------------------

    def visitCargaCSV(self, ctx):
        """Carga un archivo CSV desde disco y retorna un objeto Tabla."""
        ruta_archivo = quitar_comillas(ctx.STRING().getText())
        return Tabla.cargar_csv(ruta_archivo)

    def visitCocoGuardarCSV(self, ctx):
        """Exporta una tabla de la memoria a un archivo CSV en disco."""
        nombre_variable = ctx.ID().getText()
        ruta_destino = quitar_comillas(ctx.STRING().getText())

        linea = ctx.start.line
        columna = ctx.start.column
        tabla_a_guardar = self.memoria.obtener(nombre_variable, linea=linea, columna=columna)

        if not isinstance(tabla_a_guardar, Tabla):
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"la variable '{nombre_variable}' no es una tabla y no se puede guardar como CSV."
            )

        tabla_a_guardar.guardar_csv(ruta_destino)
        print(f"[Exportacion] Tabla '{nombre_variable}' guardada exitosamente en: '{ruta_destino}'")
        return None

    def visitFuenteCarga(self, ctx):
        """Fuente de datos por carga de archivo CSV."""
        return self.visitCargaCSV(ctx.cargaCSV())

    def visitFuenteExpresion(self, ctx):
        """Fuente de datos por expresion matematica o logica."""
        return self.visit(ctx.expresion())

    def visitFuentePipeline(self, ctx):
        """Ejecuta un encadenamiento de operaciones: datos |> op1 |> op2."""
        nombre_tabla_origen = ctx.ID().getText()
        linea = ctx.start.line
        columna = ctx.start.column

        resultado_actual = self.memoria.obtener(nombre_tabla_origen, linea=linea, columna=columna)

        for nodo_operacion in ctx.operacion():
            self.tabla_en_proceso = resultado_actual
            resultado_actual = self.visitOperacion(nodo_operacion)

        self.tabla_en_proceso = None
        return resultado_actual

    # ----------------------------------------------------------------
    # F. ASIGNACIONES, SENTENCIAS Y PROGRAMA COMPLETO
    # ----------------------------------------------------------------

    def visitAsignacion(self, ctx):
        """Ejecuta una asignacion: variable = fuente."""
        nombre_variable = ctx.ID().getText()
        valor_calculado = self.visit(ctx.cocoFuente())

        self.memoria.guardar(nombre_variable, valor_calculado)

        if isinstance(valor_calculado, Tabla):
            print(f"[Asignacion] '{nombre_variable}' -> Tabla ({len(valor_calculado.filas)} filas, columnas: {valor_calculado.columnas})")
        else:
            print(f"[Asignacion] '{nombre_variable}' = {valor_calculado}")

        return valor_calculado

    def visitSentencia(self, ctx):
        """Ejecuta una sola sentencia (asignacion, guardar o graficar)."""
        if ctx.asignacion() is not None:
            return self.visitAsignacion(ctx.asignacion())
        elif ctx.cocoGuardarCSV() is not None:
            return self.visitCocoGuardarCSV(ctx.cocoGuardarCSV())
        elif ctx.cocoGraficar() is not None:
            return self.visitCocoGraficar(ctx.cocoGraficar())
        return None

    def visitPrograma(self, ctx):
        """Ejecuta todas las sentencias del programa de principio a fin."""
        for nodo_sentencia in ctx.sentencia():
            self.visitSentencia(nodo_sentencia)
        return self.memoria
