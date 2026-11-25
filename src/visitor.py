"""Visitor e Interprete para el lenguaje Cocosette (Version Unificada).

Este modulo hereda de la clase CocosetteVisitor generada por ANTLR
y le da vida al lenguaje, ejecutando las operaciones matematicas,
logicas, de manipulacion de datos tabulares (Corte II) y las
extensiones de Machine Learning, bucles, funciones y graficacion (Corte III).

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
import ml

# Importar el modulo de graficacion de Cocosette si esta disponible
try:
    from cocograficar import graficar
except ImportError:
    try:
        from graficador import graficar
    except ImportError:
        def graficar(**kwargs):
            return f"Modulo de graficacion no encontrado para tipo '{kwargs.get('tipo')}'"


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
# 2. SEÑAL DE CONTROL DE FLUJO PARA RETORNO DE FUNCIONES
# ====================================================================


class RetornoSignal(Exception):
    """Senal de flujo para retornar un valor desde el cuerpo de una funcion."""

    def __init__(self, valor):
        super().__init__()
        self.valor = valor


# ====================================================================
# 3. CLASE INTERPRETE VISITOR (HEREDA DE COCOSSETTEVISITOR)
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

        # Diccionario donde se guardan las funciones definidas por el usuario
        self.funciones = {}

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

    def visitExpLlamada(self, ctx):
        """Evalua la llamada a una funcion dentro de una expresion matematica o logica."""
        return self.visitLlamadaFuncion(ctx.llamadaFuncion())

    def visitExpLlamadaML(self, ctx):
        """Evalua una llamada de Machine Learning o calcular dentro de una expresion."""
        return self.visit(ctx.cocoLlamadaML())

    def visitCocoLlamadaML(self, ctx):
        """Enruta la llamada de ML hacia su regla especifica."""
        return self.visitChildren(ctx)

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
        """Genera una grafica PNG a partir de una tabla en memoria."""
        linea = ctx.start.line
        columna = ctx.start.column

        # Obtener el nombre de la variable de tabla (compatible con etiqueta 'tabla' o posicional 'ID(0)')
        if hasattr(ctx, "tabla") and ctx.tabla is not None:
            nombre = ctx.tabla.text
        elif ctx.ID() is not None and len(ctx.ID()) > 0:
            nombre = ctx.ID(0).getText()
        else:
            raise ValueError(f"Error sintactico (linea {linea}, columna {columna}): no se especifico tabla para graficar.")

        tabla = self.memoria.obtener(nombre, linea=linea, columna=columna)

        if not isinstance(tabla, Tabla):
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"'{nombre}' no es una tabla y no se puede graficar."
            )

        def texto(token):
            """Token opcional -> cadena sin comillas, o None si no se escribio."""
            return quitar_comillas(token.text) if token is not None else None

        # Obtener nombres de columnas X e Y (compatible con etiquetas o posicional)
        if hasattr(ctx, "colx") and ctx.colx is not None:
            col_x = ctx.colx.text
        elif ctx.ID() is not None and len(ctx.ID()) > 1:
            col_x = ctx.ID(1).getText()
        else:
            col_x = None

        if hasattr(ctx, "coly") and ctx.coly is not None:
            col_y = ctx.coly.text
        elif ctx.ID() is not None and len(ctx.ID()) > 2:
            col_y = ctx.ID(2).getText()
        else:
            col_y = None

        # Modelo entrenado opcional
        modelo = None
        if hasattr(ctx, "modelo") and ctx.modelo is not None:
            nombre_modelo = ctx.modelo.text
            modelo = self.memoria.obtener(nombre_modelo, linea=linea, columna=columna)

            if not isinstance(modelo, dict) or "tipo" not in modelo:
                raise TypeError(
                    f"Error semantico (linea {linea}, columna {columna}): "
                    f"'{nombre_modelo}' no es un modelo entrenado."
                )

        titulo_val = texto(ctx.titulo) if hasattr(ctx, "titulo") and ctx.titulo is not None else None
        etx_val = texto(ctx.etx) if hasattr(ctx, "etx") and ctx.etx is not None else None
        ety_val = texto(ctx.ety) if hasattr(ctx, "ety") and ctx.ety is not None else None
        leyenda_val = texto(ctx.leyenda) if hasattr(ctx, "leyenda") and ctx.leyenda is not None else None
        ruta_val = texto(ctx.ruta) if hasattr(ctx, "ruta") and ctx.ruta is not None else None

        # Si no se usaron etiquetas, buscar cadenas posicionales
        if ctx.STRING() is not None and len(ctx.STRING()) > 0:
            if titulo_val is None and hasattr(ctx, "COCOTITULO") and ctx.COCOTITULO() is not None:
                titulo_val = quitar_comillas(ctx.STRING(0).getText())
            if ruta_val is None and hasattr(ctx, "COCOGUARDAR") and ctx.COCOGUARDAR() is not None:
                idx_ruta = len(ctx.STRING()) - 1
                ruta_val = quitar_comillas(ctx.STRING(idx_ruta).getText())

        # Recoge errores y los reporta con linea y columna de la sentencia de graficar
        try:
            mensaje = graficar(
                tipo=ctx.cocoGrafica().getText(),
                tabla=tabla,
                x=col_x,
                y=col_y,
                titulo=titulo_val,
                etiqueta_x=etx_val,
                etiqueta_y=ety_val,
                leyenda=leyenda_val,
                ruta=ruta_val,
                modelo=modelo,
            )
        except (KeyError, TypeError, ValueError) as error:
            detalle = error.args[0] if error.args else str(error)
            raise ValueError(f"{detalle} (linea {linea}, columna {columna})")

        print(f"[Grafica] {mensaje}")
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
    # F. ASIGNACIONES, SENTENCIAS Y CONTROL DE FLUJO
    # ----------------------------------------------------------------

    def visitAsignacion(self, ctx):
        """Ejecuta una asignacion: variable = fuente."""
        nombre_variable = ctx.ID().getText()
        valor_calculado = self.visit(ctx.cocoFuente())

        self.memoria.guardar(nombre_variable, valor_calculado)
        return valor_calculado

    def visitCocoImprimir(self, ctx):
        """Imprime el resultado de una expresion o tabla en consola."""
        valor = self.visit(ctx.expresion())
        if isinstance(valor, Tabla):
            valor.mostrar()
        elif isinstance(valor, dict) and "tipo" in valor:
            if valor["tipo"] == "lineal":
                print(f"y = {valor['m']} * x + {valor['b']}")
            elif valor["tipo"] == "polinomial":
                print(f"y = {valor['a']} * x^2 + {valor['b']} * x + {valor['c']}")
            elif valor["tipo"] == "perceptron":
                w = valor["pesos"]
                b = valor["sesgo"]
                print(f"Neurona(w1={w[0]}, w2={w[1]}, sesgo={b})")
            else:
                print(valor)
        else:
            print(valor)
        return valor

    def visitCocoMientras(self, ctx):
        """Ejecuta un bucle mientras la expresion condicion sea verdadera."""
        while bool(self.visit(ctx.expresion())):
            for nodo_sentencia in ctx.sentencia():
                self.visitSentencia(nodo_sentencia)
        return None

    def visitCocoDefFuncion(self, ctx):
        """Guarda la declaracion de una funcion (receta) en el diccionario de funciones."""
        nombre_func = ctx.ID().getText()
        params = []
        if ctx.listaParams() is not None:
            params = [nodo_id.getText() for nodo_id in ctx.listaParams().ID()]

        self.funciones[nombre_func] = {
            "params": params,
            "cuerpo": ctx.sentencia()
        }
        return None

    def visitCocoRetornar(self, ctx):
        """Lanza la senal de retorno con el valor evaluado de la expresion."""
        if ctx.expresion() is not None:
            valor = self.visit(ctx.expresion())
        else:
            valor = None
        raise RetornoSignal(valor)

    def visitLlamadaFuncion(self, ctx):
        """Ejecuta la llamada a una funcion con argumentos y ambito local."""
        nombre_func = ctx.ID().getText()
        linea = ctx.start.line
        columna = ctx.start.column

        if nombre_func not in self.funciones:
            raise NameError(
                f"Error semantico (linea {linea}, columna {columna}): la funcion '{nombre_func}' no ha sido definida."
            )

        receta = self.funciones[nombre_func]
        nombres_params = receta["params"]
        cuerpo = receta["cuerpo"]

        valores_args = []
        if ctx.listaArgumentos() is not None:
            for exp in ctx.listaArgumentos().expresion():
                valores_args.append(self.visit(exp))

        if len(valores_args) != len(nombres_params):
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): la funcion '{nombre_func}' "
                f"espera {len(nombres_params)} argumento(s), pero se pasaron {len(valores_args)}."
            )

        memoria_previa = self.memoria
        memoria_local = MemoriaEjecucion(padre=memoria_previa)

        for param, val in zip(nombres_params, valores_args):
            memoria_local.guardar(param, val)

        self.memoria = memoria_local
        resultado = None

        try:
            for nodo_sentencia in cuerpo:
                self.visitSentencia(nodo_sentencia)
        except RetornoSignal as senal:
            resultado = senal.valor
        finally:
            self.memoria = memoria_previa

        return resultado

    # ----------------------------------------------------------------
    # G. CORTE III: MACHINE LEARNING Y EVALUACION (REGRESION, PERCEPTRON)
    # ----------------------------------------------------------------

    def _evaluar_param_columna(self, exp_ctx):
        """Evalua un parametro de columna, admitiendo string con comillas o identificador sin comillas."""
        if hasattr(exp_ctx, "ID") and exp_ctx.ID() is not None and not hasattr(exp_ctx, "op"):
            nombre_id = exp_ctx.ID().getText()
            if self.memoria.existe(nombre_id):
                return str(self.memoria.obtener(nombre_id))
            return nombre_id
        val = self.visit(exp_ctx)
        return str(val)

    def _extraer_vector_numerico(self, tabla: Tabla, nombre_col: str, linea: int, columna: int):
        """Extrae los valores numericos de una columna de una tabla."""
        if not isinstance(tabla, Tabla):
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"el primer argumento debe ser una Tabla, pero se recibio {type(tabla).__name__}."
            )
        if nombre_col not in tabla.columnas:
            raise ValueError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"la columna '{nombre_col}' no existe en la tabla. Columnas disponibles: {tabla.columnas}."
            )
        valores = []
        for f in tabla.filas:
            v = f.get(nombre_col)
            if v is None or v == "":
                continue
            try:
                valores.append(float(v))
            except (ValueError, TypeError):
                continue
        return valores

    def visitCocoRegresionLineal(self, ctx):
        """Entrena una regresion lineal: regresion_lineal(tabla, col_x, col_y, [tasa], [epocas])."""
        linea = ctx.start.line
        columna = ctx.start.column
        lista_exp = ctx.listaArgumentos().expresion() if ctx.listaArgumentos() else []

        if len(lista_exp) < 3:
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"'regresion_lineal' requiere al menos 3 argumentos: (tabla, columna_x, columna_y)."
            )

        tabla = self.visit(lista_exp[0])
        col_x = self._evaluar_param_columna(lista_exp[1])
        col_y = self._evaluar_param_columna(lista_exp[2])

        tasa = float(self.visit(lista_exp[3])) if len(lista_exp) > 3 else 0.01
        epocas = int(self.visit(lista_exp[4])) if len(lista_exp) > 4 else 1000

        x_vals = self._extraer_vector_numerico(tabla, col_x, linea, columna)
        y_vals = self._extraer_vector_numerico(tabla, col_y, linea, columna)

        return ml.entrenar_regresion_lineal(x_vals, y_vals, tasa=tasa, epocas=epocas)

    def visitCocoRegresionPoli(self, ctx):
        """Entrena una regresion polinomial: regresion_polinomial(tabla, col_x, col_y)."""
        linea = ctx.start.line
        columna = ctx.start.column
        lista_exp = ctx.listaArgumentos().expresion() if ctx.listaArgumentos() else []

        if len(lista_exp) < 3:
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"'regresion_polinomial' requiere al menos 3 argumentos: (tabla, columna_x, columna_y)."
            )

        tabla = self.visit(lista_exp[0])
        col_x = self._evaluar_param_columna(lista_exp[1])
        col_y = self._evaluar_param_columna(lista_exp[2])

        x_vals = self._extraer_vector_numerico(tabla, col_x, linea, columna)
        y_vals = self._extraer_vector_numerico(tabla, col_y, linea, columna)

        return ml.entrenar_regresion_polinomial(x_vals, y_vals)

    def visitCocoPerceptron(self, ctx):
        """Crea o entrena un perceptron:
        - Manual: perceptron(w1, w2, b)
        - Entrenamiento: perceptron(tabla, col_x1, col_x2, col_y, [tasa], [epocas])
        """
        linea = ctx.start.line
        columna = ctx.start.column
        lista_exp = ctx.listaArgumentos().expresion() if ctx.listaArgumentos() else []

        if len(lista_exp) == 3:
            arg0 = self.visit(lista_exp[0])
            if not isinstance(arg0, Tabla):
                w1 = float(arg0)
                w2 = float(self.visit(lista_exp[1]))
                b = float(self.visit(lista_exp[2]))
                return ml.crear_perceptron_manual(w1, w2, b)

        if len(lista_exp) < 4:
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"'perceptron' espera 3 argumentos numericos (w1, w2, b) o al menos 4 (tabla, x1, x2, y)."
            )

        tabla = self.visit(lista_exp[0])
        col_x1 = self._evaluar_param_columna(lista_exp[1])
        col_x2 = self._evaluar_param_columna(lista_exp[2])
        col_y = self._evaluar_param_columna(lista_exp[3])

        tasa = float(self.visit(lista_exp[4])) if len(lista_exp) > 4 else 0.1
        epocas = int(self.visit(lista_exp[5])) if len(lista_exp) > 5 else 1000

        x1_vals = self._extraer_vector_numerico(tabla, col_x1, linea, columna)
        x2_vals = self._extraer_vector_numerico(tabla, col_x2, linea, columna)
        y_vals = self._extraer_vector_numerico(tabla, col_y, linea, columna)

        return ml.entrenar_perceptron(x1_vals, x2_vals, y_vals, tasa=tasa, epocas=epocas)

    def visitCocoCalcular(self, ctx):
        """Evalua un modelo con datos de entrada: calcular(modelo, x) o calcular(neurona, x1, x2)."""
        linea = ctx.start.line
        columna = ctx.start.column
        lista_exp = ctx.listaArgumentos().expresion() if ctx.listaArgumentos() else []

        if len(lista_exp) < 2:
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"'calcular' requiere al menos un modelo y una entrada: calcular(modelo, ...)."
            )

        modelo = self.visit(lista_exp[0])
        if not isinstance(modelo, dict) or "tipo" not in modelo:
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"el primer argumento de 'calcular' debe ser un modelo o ecuacion valida, no {type(modelo).__name__}."
            )

        tipo_mod = modelo["tipo"]
        valores = [self.visit(exp) for exp in lista_exp[1:]]

        if tipo_mod == "lineal":
            if len(valores) != 1:
                raise TypeError(
                    f"Error semantico (linea {linea}, columna {columna}): "
                    f"la ecuacion lineal espera 1 variable x, pero se pasaron {len(valores)}."
                )
            x = float(valores[0])
            res = modelo["m"] * x + modelo["b"]
            return round(res, 2)

        elif tipo_mod == "polinomial":
            if len(valores) != 1:
                raise TypeError(
                    f"Error semantico (linea {linea}, columna {columna}): "
                    f"la ecuacion polinomial espera 1 variable x, pero se pasaron {len(valores)}."
                )
            x = float(valores[0])
            res = modelo["a"] * (x ** 2) + modelo["b"] * x + modelo["c"]
            return round(res, 2)

        elif tipo_mod == "perceptron":
            pesos = modelo["pesos"]
            sesgo = modelo["sesgo"]
            if len(valores) != len(pesos):
                raise TypeError(
                    f"Error semantico (linea {linea}, columna {columna}): "
                    f"el perceptron espera {len(pesos)} entrada(s), pero se pasaron {len(valores)}."
                )
            z = sum(float(w) * float(x) for w, x in zip(pesos, valores)) + float(sesgo)
            return 1 if z >= 0 else 0

        else:
            raise ValueError(
                f"Error semantico (linea {linea}, columna {columna}): tipo de modelo '{tipo_mod}' desconocido."
            )

    # ----------------------------------------------------------------
    # H. SENTENCIAS Y PROGRAMA COMPLETO
    # ----------------------------------------------------------------

    def visitSentencia(self, ctx):
        """Ejecuta una sola sentencia (asignacion, guardar, graficar, imprimir, funcion o expresion)."""
        if ctx.asignacion() is not None:
            return self.visitAsignacion(ctx.asignacion())
        elif ctx.cocoGuardarCSV() is not None:
            return self.visitCocoGuardarCSV(ctx.cocoGuardarCSV())
        elif ctx.cocoGraficar() is not None:
            return self.visitCocoGraficar(ctx.cocoGraficar())
        elif ctx.cocoImprimir() is not None:
            return self.visitCocoImprimir(ctx.cocoImprimir())
        elif ctx.cocoDefFuncion() is not None:
            return self.visitCocoDefFuncion(ctx.cocoDefFuncion())
        elif ctx.cocoRetornar() is not None:
            return self.visitCocoRetornar(ctx.cocoRetornar())
        elif ctx.cocoMientras() is not None:
            return self.visitCocoMientras(ctx.cocoMientras())
        elif ctx.expresion() is not None:
            return self.visit(ctx.expresion())
        return None

    def visitPrograma(self, ctx):
        """Ejecuta todas las sentencias del programa de principio a fin."""
        for nodo_sentencia in ctx.sentencia():
            self.visitSentencia(nodo_sentencia)
        return self.memoria
