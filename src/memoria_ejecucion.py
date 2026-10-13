"""Memoria de ejecucion (Tabla de simbolos) para el interprete de Cocosette.

Este modulo administra las variables que se van creando durante la ejecucion
de un programa en el DSL. Es simplemente un diccionario inteligente que guarda
los valores y avisa con un error semantico si alguien intenta usar una variable
que no existe.
"""


class MemoriaEjecucion:
    """Administra las variables en memoria RAM durante la ejecucion."""

    def __init__(self):
        # Diccionario interno donde se guardan las variables:
        # clave: nombre de la variable (ej. "ventas", "precio_minimo")
        # valor: el dato real (ej. un objeto Tabla, un numero, un texto)
        self.variables = {}

    def guardar(self, nombre, valor):
        """Guarda o actualiza una variable en memoria.

        Equivale a la asignacion en el DSL: variable = expresion;
        """
        self.variables[nombre] = valor

    def obtener(self, nombre, linea=None, columna=None):
        """Busca una variable en la memoria y devuelve su valor.

        Si la variable no existe, lanza un Error Semantico claro.
        """
        if nombre not in self.variables:
            posicion = ""
            if linea is not None:
                posicion = f" (linea {linea}, columna {columna})" if columna is not None else f" (linea {linea})"

            raise NameError(
                f"Error semantico{posicion}: la variable '{nombre}' no ha sido declarada."
            )

        return self.variables[nombre]

    def existe(self, nombre):
        """Comprueba si una variable ya fue creada (devuelve True o False)."""
        return nombre in self.variables

    def limpiar(self):
        """Borra todas las variables de la memoria."""
        self.variables.clear()

    def __repr__(self):
        """Permite imprimir la memoria en consola para ver que tiene guardado."""
        if not self.variables:
            return "[Memoria vacia]"

        lineas = ["--- Variables en Memoria ---"]
        for nombre, valor in self.variables.items():
            tipo = type(valor).__name__
            # Si el valor es una Tabla, mostramos cuantas filas tiene
            if hasattr(valor, "filas"):
                info = f"Tabla con {len(valor.filas)} registros"
            else:
                info = repr(valor)
            lineas.append(f"  * {nombre} ({tipo}) = {info}")
        return "\n".join(lineas)


# Alias por si el profesor pregunta por el nombre academico tradicional:
TablaDeSimbolos = MemoriaEjecucion
