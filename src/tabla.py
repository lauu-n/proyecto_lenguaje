"""Motor de datos tabular implementado en Python puro (sin librerias externas).

Este modulo provee la clase `Tabla`, disenada para modelar la semantica
de las operaciones del DSL Cocosette: carga, filtrado, seleccion, transformacion,
agrupamiento, calculo de estadisticas y exportacion a CSV.

Utiliza exclusivamente la biblioteca estandar de Python:
- `csv`: para la lectura y escritura de archivos de texto plano.
- `math`: para funciones matematicas elementales (como raiz cuadrada).
"""

import csv
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class Tabla:
    """Representa una estructura de datos tabular en memoria (filas y columnas).

    Diseño inmutable: cada operacion de transformacion retorna una NUEVA instancia
    de Tabla, preservando la original para asegurar que los pipelines sean reproducibles
    y no tengan efectos secundarios indeseados.
    """

    def __init__(self, columnas: List[str], filas: List[Dict[str, Any]]):
        """Inicializa una tabla.

        Args:
            columnas: Lista con los nombres de las columnas en orden.
            filas: Lista de diccionarios, donde cada diccionario representa una fila
                   con pares {nombre_columna: valor}.
        """
        self.columnas: List[str] = list(columnas)
        self.filas: List[Dict[str, Any]] = [dict(fila) for fila in filas]

    # ================================================================
    # 1. CARGA Y EXPORTACIÓN (I/O)
    # ================================================================

    @classmethod
    def cargar_csv(cls, ruta_archivo: str, separador: str = ",") -> "Tabla":
        """Carga un archivo CSV desde disco infiriendo tipos basicos.

        Convierte automaticamente:
        - Enteros ('10' -> 10)
        - Decimales ('10.5' -> 10.5)
        - Booleanos ('verdadero'/'true' -> True, 'falso'/'false' -> False)
        - Nulos (vacios '' -> None)
        - Cadenas de texto ordinarias
        """
        filas_procesadas: List[Dict[str, Any]] = []
        columnas: List[str] = []

        with open(ruta_archivo, mode="r", encoding="utf-8-sig") as f:
            lector = csv.reader(f, delimiter=separador)
            encabezados = next(lector, None)
            if encabezados is None:
                return cls([], [])

            columnas = [col.strip() for col in encabezados]

            for num_fila, fila_cruda in enumerate(lector, start=2):
                if not fila_cruda or all(campo.strip() == "" for campo in fila_cruda):
                    continue  # Ignorar lineas totalmente vacias

                fila_dict: Dict[str, Any] = {}
                for idx, col in enumerate(columnas):
                    valor_crudo = fila_cruda[idx].strip() if idx < len(fila_cruda) else ""
                    fila_dict[col] = cls._inferir_tipo(valor_crudo)
                filas_procesadas.append(fila_dict)

        return cls(columnas, filas_procesadas)

    def guardar_csv(self, ruta_archivo: str, separador: str = ",") -> None:
        """Exporta la tabla actual a un archivo CSV en disco."""
        with open(ruta_archivo, mode="w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f, delimiter=separador)
            escritor.writerow(self.columnas)
            for fila in self.filas:
                fila_serializada = []
                for col in self.columnas:
                    val = fila.get(col, "")
                    if val is None:
                        fila_serializada.append("")
                    elif isinstance(val, bool):
                        fila_serializada.append("verdadero" if val else "falso")
                    else:
                        fila_serializada.append(str(val))
                escritor.writerow(fila_serializada)

    @staticmethod
    def _inferir_tipo(valor: str) -> Any:
        """Convierte una cadena de texto al tipo nativo de Python mas representativo."""
        if valor == "" or valor.lower() in ("null", "none", "nan"):
            return None
        if valor.lower() in ("verdadero", "true"):
            return True
        if valor.lower() in ("falso", "false"):
            return False

        # Intentar entero
        try:
            return int(valor)
        except ValueError:
            pass

        # Intentar decimal
        try:
            return float(valor)
        except ValueError:
            pass

        # Dejar como texto
        return valor

    # ================================================================
    # 2. SELECCIÓN, FILTRADO Y TRANSFORMACIÓN (PIPELINE)
    # ================================================================

    def seleccionar(self, columnas_deseadas: List[str]) -> "Tabla":
        """Retorna una nueva tabla que solo contiene las columnas especificadas."""
        self._validar_columnas(columnas_deseadas)
        nuevas_filas = [
            {col: fila.get(col) for col in columnas_deseadas}
            for fila in self.filas
        ]
        return Tabla(columnas_deseadas, nuevas_filas)

    def filtrar(self, predicado: Callable[[Dict[str, Any]], bool]) -> "Tabla":
        """Filtra las filas mediante una funcion o condicion booleana."""
        filas_filtradas = [fila for fila in self.filas if predicado(fila)]
        return Tabla(self.columnas, filas_filtradas)

    def crear_columna(self, nombre_columna: str, funcion_calculo: Callable[[Dict[str, Any]], Any]) -> "Tabla":
        """Calcula y anade una nueva columna a partir de una expresion aplicada fila por fila."""
        nuevas_columnas = list(self.columnas)
        if nombre_columna not in nuevas_columnas:
            nuevas_columnas.append(nombre_columna)

        nuevas_filas = []
        for fila in self.filas:
            fila_copia = dict(fila)
            fila_copia[nombre_columna] = funcion_calculo(fila)
            nuevas_filas.append(fila_copia)

        return Tabla(nuevas_columnas, nuevas_filas)

    def ordenar(self, columna: str, ascendente: bool = True) -> "Tabla":
        """Ordena las filas segun el valor de una columna especifica."""
        self._validar_columnas([columna])

        def criterio_orden(fila: Dict[str, Any]) -> Any:
            val = fila.get(columna)
            # Manejo de nulos para no romper la comparacion en Python
            if val is None:
                return (1, 0) if ascendente else (0, 0)
            return (0, val)

        filas_ordenadas = sorted(self.filas, key=criterio_orden, reverse=not ascendente)
        return Tabla(self.columnas, filas_ordenadas)

    def renombrar(self, columna_origen: str, columna_nueva: str) -> "Tabla":
        """Cambia el nombre de una columna existente."""
        self._validar_columnas([columna_origen])
        nuevas_columnas = [
            columna_nueva if col == columna_origen else col
            for col in self.columnas
        ]
        nuevas_filas = []
        for fila in self.filas:
            fila_copia = {}
            for col, val in fila.items():
                if col == columna_origen:
                    fila_copia[columna_nueva] = val
                else:
                    fila_copia[col] = val
            nuevas_filas.append(fila_copia)
        return Tabla(nuevas_columnas, nuevas_filas)

    def eliminar_duplicados(self) -> "Tabla":
        """Elimina filas exactamente repetidas conservando el orden de aparicion."""
        filas_unicas: List[Dict[str, Any]] = []
        vistos = set()

        for fila in self.filas:
            # Crear tupla inmutable de los valores para comparar eficientemente
            clave = tuple(fila.get(col) for col in self.columnas)
            if clave not in vistos:
                vistos.add(clave)
                filas_unicas.append(fila)

        return Tabla(self.columnas, filas_unicas)

    def eliminar_nulos(self) -> "Tabla":
        """Elimina cualquier fila que contenga un valor None en alguna columna."""
        filas_limpias = [
            fila for fila in self.filas
            if not any(fila.get(col) is None for col in self.columnas)
        ]
        return Tabla(self.columnas, filas_limpias)

    def rellenar_nulos(self, columna: str, valor_reemplazo: Any) -> "Tabla":
        """Reemplaza los valores nulos (None) en una columna especifica por un valor fijo."""
        self._validar_columnas([columna])
        nuevas_filas = []
        for fila in self.filas:
            fila_copia = dict(fila)
            if fila_copia.get(columna) is None:
                fila_copia[columna] = valor_reemplazo
            nuevas_filas.append(fila_copia)
        return Tabla(self.columnas, nuevas_filas)

    def convertir(self, columna: str, tipo_destino: str) -> "Tabla":
        """Convierte los tipos de datos de una columna ('entero', 'decimal', 'texto', 'booleano')."""
        self._validar_columnas([columna])
        tipo = tipo_destino.lower()
        nuevas_filas = []

        for fila in self.filas:
            fila_copia = dict(fila)
            val = fila_copia.get(columna)
            if val is not None:
                try:
                    if tipo in ("entero", "int"):
                        fila_copia[columna] = int(float(val))
                    elif tipo in ("decimal", "float"):
                        fila_copia[columna] = float(val)
                    elif tipo in ("texto", "str"):
                        fila_copia[columna] = str(val)
                    elif tipo in ("booleano", "bool"):
                        fila_copia[columna] = bool(val)
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        f"No se pudo convertir el valor '{val}' en columna '{columna}' al tipo '{tipo}': {e}"
                    )
            nuevas_filas.append(fila_copia)

        return Tabla(self.columnas, nuevas_filas)

    # ================================================================
    # 3. AGRUPAMIENTO Y AGREGACIONES (CORTE II)
    # ================================================================

    def agrupar_por(self, columnas_grupo: List[str]) -> "AgrupacionTabla":
        """Prepara la tabla para calcular agregaciones agrupadas."""
        self._validar_columnas(columnas_grupo)
        return AgrupacionTabla(self, columnas_grupo)

    def _validar_columnas(self, cols: List[str]) -> None:
        """Comprueba semánticamente si las columnas existen en la tabla."""
        for col in cols:
            if col not in self.columnas:
                raise KeyError(f"Error semántico: la columna '{col}' no existe en la tabla. Columnas disponibles: {self.columnas}")

    # ================================================================
    # 4. REPRESENTACIÓN Y VISUALIZACIÓN EN CONSOLA
    # ================================================================

    def __len__(self) -> int:
        return len(self.filas)

    def mostrar(self, max_filas: int = 10) -> str:
        """Formatea la tabla como texto estructurado tipo cuadrícula para la consola."""
        if not self.columnas:
            return "[Tabla vacia]"

        filas_mostrar = self.filas[:max_filas]

        # Calcular ancho de cada columna
        anchos = {}
        for col in self.columnas:
            longitudes = [len(str(col))]
            for fila in filas_mostrar:
                longitudes.append(len(str(fila.get(col, ""))))
            anchos[col] = max(longitudes)

        # Linea divisoria
        separador = "+-" + "-+-".join("-" * anchos[col] for col in self.columnas) + "-+"

        lineas = [separador]
        # Encabezados
        encabezado = "| " + " | ".join(col.ljust(anchos[col]) for col in self.columnas) + " |"
        lineas.append(encabezado)
        lineas.append(separador)

        # Filas
        for fila in filas_mostrar:
            vals = []
            for col in self.columnas:
                v = fila.get(col, "")
                texto_v = "null" if v is None else str(v)
                vals.append(texto_v.ljust(anchos[col]))
            lineas.append("| " + " | ".join(vals) + " |")

        lineas.append(separador)
        if len(self.filas) > max_filas:
            lineas.append(f"... mostrando {max_filas} de {len(self.filas)} registros")
        else:
            lineas.append(f"Total: {len(self.filas)} registros")

        return "\n".join(lineas)

    def __repr__(self) -> str:
        return self.mostrar(max_filas=5)


# ================================================================
# CLASE AUXILIAR: AgrupacionTabla
# ================================================================

class AgrupacionTabla:
    """Maneja las particiones de filas resultantes de una operacion 'agrupar por'."""

    def __init__(self, tabla_origen: Tabla, columnas_grupo: List[str]):
        self.tabla_origen = tabla_origen
        self.columnas_grupo = list(columnas_grupo)
        self.grupos: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
        self._construir_grupos()

    def _construir_grupos(self) -> None:
        """Divide las filas en cubetas segun la combinacion de valores de las columnas agrupadoras."""
        for fila in self.tabla_origen.filas:
            clave = tuple(fila.get(col) for col in self.columnas_grupo)
            if clave not in self.grupos:
                self.grupos[clave] = []
            self.grupos[clave].append(fila)

    def resumir(self, especificaciones: List[Tuple[str, str, Optional[str]]]) -> Tabla:
        """Aplica funciones de agregacion sobre cada grupo.

        Args:
            especificaciones: Lista de tuplas con el formato:
                (nombre_nueva_columna, funcion_agregacion, columna_origen_o_None)
                Ejemplo:
                [
                    ("ingreso_total", "suma", "total"),
                    ("promedio_precio", "media", "precio"),
                    ("total_registros", "contar", None)
                ]

        Returns:
            Una nueva Tabla con las columnas de agrupacion mas las columnas calculadas.
        """
        nuevas_columnas = list(self.columnas_grupo) + [esp[0] for esp in especificaciones]
        filas_resumen: List[Dict[str, Any]] = []

        for clave_grupo, filas_del_grupo in self.grupos.items():
            fila_resumen: Dict[str, Any] = {}

            # 1. Asignar los valores de las columnas agrupadoras
            for idx, col_grupo in enumerate(self.columnas_grupo):
                fila_resumen[col_grupo] = clave_grupo[idx]

            # 2. Calcular cada funcion de agregacion
            for nombre_salida, funcion_nombre, col_origen in especificaciones:
                fila_resumen[nombre_salida] = self._calcular_agregacion(
                    funcion_nombre, col_origen, filas_del_grupo
                )

            filas_resumen.append(fila_resumen)

        return Tabla(nuevas_columnas, filas_resumen)

    @staticmethod
    def _calcular_agregacion(funcion: str, col: Optional[str], filas: List[Dict[str, Any]]) -> Any:
        """Calcula el valor estadistico usando matematicas elementales y Python puro."""
        func = funcion.lower()

        if func == "contar":
            return len(filas)

        if col is None:
            raise ValueError(f"La funcion de agregacion '{func}' requiere especificar una columna.")

        # Extraer valores ignorando nulos
        valores = [fila.get(col) for fila in filas if fila.get(col) is not None]

        if not valores:
            return 0 if func in ("suma", "contar") else None

        # Convertir a flotantes si aplica
        numeros = []
        for v in valores:
            if isinstance(v, (int, float)):
                numeros.append(float(v))
            else:
                try:
                    numeros.append(float(v))
                except (ValueError, TypeError):
                    pass

        if func == "suma":
            return sum(numeros) if numeros else 0

        if func == "media":
            return (sum(numeros) / len(numeros)) if numeros else None

        if func == "mediana":
            if not numeros:
                return None
            numeros_ordenados = sorted(numeros)
            n = len(numeros_ordenados)
            mitad = n // 2
            if n % 2 == 1:
                return numeros_ordenados[mitad]
            return (numeros_ordenados[mitad - 1] + numeros_ordenados[mitad]) / 2.0

        if func == "minimo":
            return min(numeros) if numeros else None

        if func == "maximo":
            return max(numeros) if numeros else None

        if func in ("desviacion_estandar", "desviacionest", "desvest"):
            # Calculo de desviacion estandar muestral: sqrt( sum((x - media)^2) / (n - 1) )
            if len(numeros) < 2:
                return 0.0
            media = sum(numeros) / len(numeros)
            varianza = sum((x - media) ** 2 for x in numeros) / (len(numeros) - 1)
            return math.sqrt(varianza)

        raise ValueError(f"Funcion de agregacion desconocida: '{func}'")
