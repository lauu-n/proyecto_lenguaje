"""Visitor consolidado para el lenguaje Cocosette.

Reutiliza la implementacion común y las funcionalidades adicionales de
``visitor1.py`` (funciones, ML, expresiones, tablas y sentencias), e integra
las funcionalidades propias de ``visitor0.py`` para graficar y reportar
asignaciones.
"""

import sys

# Mantener disponibles los módulos generados y auxiliares en los mismos
# entornos desde los que se ejecutan los visitors existentes.
sys.path.append("src/parser")
sys.path.append("src")
sys.path.append("parser")

from cocograficar import graficar
from tabla import Tabla
from visitor1 import InterpreteVisitor as _InterpreteVisitor
from visitor1 import quitar_comillas


class InterpreteVisitor(_InterpreteVisitor):
    """Visitor consolidado que reúne las funcionalidades de ambos visitors."""

    def visitCocoGraficar(self, ctx):
        """Genera una gráfica PNG a partir de una tabla en memoria."""
        linea = ctx.start.line
        columna = ctx.start.column
        nombre = ctx.tabla.text
        tabla = self.memoria.obtener(nombre, linea=linea, columna=columna)

        if not isinstance(tabla, Tabla):
            raise TypeError(
                f"Error semantico (linea {linea}, columna {columna}): "
                f"'{nombre}' no es una tabla y no se puede graficar."
            )

        def texto(token):
            """Convierte un token opcional a texto sin comillas."""
            return quitar_comillas(token.text) if token is not None else None

        modelo = None
        if ctx.modelo is not None:
            nombre_modelo = ctx.modelo.text
            modelo = self.memoria.obtener(
                nombre_modelo,
                linea=linea,
                columna=columna,
            )

            if not isinstance(modelo, dict) or "tipo" not in modelo:
                raise TypeError(
                    f"Error semantico (linea {linea}, columna {columna}): "
                    f"'{nombre_modelo}' no es un modelo entrenado."
                )

        try:
            mensaje = graficar(
                tipo=ctx.cocoGrafica().getText(),
                tabla=tabla,
                x=ctx.colx.text,
                y=ctx.coly.text if ctx.coly is not None else None,
                titulo=texto(ctx.titulo),
                etiqueta_x=texto(ctx.etx),
                etiqueta_y=texto(ctx.ety),
                leyenda=texto(ctx.leyenda),
                ruta=texto(ctx.ruta),
                modelo=modelo,
            )
        except (KeyError, TypeError, ValueError) as error:
            detalle = error.args[0] if error.args else str(error)
            raise ValueError(f"{detalle} (linea {linea}, columna {columna})") from error

        print(f"[Grafica] {mensaje}")
        return None

    def visitAsignacion(self, ctx):
        """Evalúa y guarda una asignación, informando el valor asignado."""
        nombre_variable = ctx.ID().getText()
        valor_calculado = self.visit(ctx.cocoFuente())
        self.memoria.guardar(nombre_variable, valor_calculado)

        if isinstance(valor_calculado, Tabla):
            print(
                f"[Asignacion] '{nombre_variable}' -> Tabla "
                f"({len(valor_calculado.filas)} filas, "
                f"columnas: {valor_calculado.columnas})"
            )
        else:
            print(f"[Asignacion] '{nombre_variable}' = {valor_calculado}")

        return valor_calculado
