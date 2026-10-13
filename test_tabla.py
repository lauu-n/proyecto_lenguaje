"""Pruebas unitarias y de funcionamiento para la clase Tabla (Python puro)."""

import sys
from pathlib import Path

# Anadir src al path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from tabla import Tabla


def main():
    print("=" * 60)
    print("1. CARGA DE CSV (datos/ventas.csv)")
    print("=" * 60)
    tabla = Tabla.cargar_csv("datos/ventas.csv")
    print(tabla.mostrar(max_filas=5))
    print(f"Total registros cargados: {len(tabla)}")
    print(f"Columnas detectadas: {tabla.columnas}\n")

    print("=" * 60)
    print("2. SELECCIÓN DE COLUMNAS")
    print("=" * 60)
    seleccionada = tabla.seleccionar(["fecha", "ciudad", "categoria", "unidades", "precio"])
    print(seleccionada.mostrar(max_filas=3))
    print()

    print("=" * 60)
    print("3. FILTRADO (unidades > 5 y precio >= 1000)")
    print("=" * 60)
    filtrada = seleccionada.filtrar(lambda f: f["unidades"] > 5 and f["precio"] >= 1000)
    print(filtrada.mostrar(max_filas=3))
    print(f"Filas resultantes: {len(filtrada)}\n")

    print("=" * 60)
    print("4. CREACIÓN DE COLUMNA CALCULADA (total = unidades * precio)")
    print("=" * 60)
    con_total = filtrada.crear_columna("total", lambda f: f["unidades"] * f["precio"])
    print(con_total.mostrar(max_filas=3))
    print()

    print("=" * 60)
    print("5. ORDENAMIENTO (ordenar por total DESC)")
    print("=" * 60)
    ordenada = con_total.ordenar("total", ascendente=False)
    print(ordenada.mostrar(max_filas=4))
    print()

    print("=" * 60)
    print("6. RENOMBRAR COLUMNA (total -> total_venta)")
    print("=" * 60)
    renombrada = ordenada.renombrar("total", "total_venta")
    print(renombrada.mostrar(max_filas=3))
    print()

    print("=" * 60)
    print("7. AGRUPAMIENTO Y RESUMEN (agrupar por [ciudad] |> resumir)")
    print("=" * 60)
    resumen = con_total.agrupar_por(["ciudad"]).resumir([
        ("ingreso_total", "suma", "total"),
        ("promedio_precio", "media", "precio"),
        ("mediana_total", "mediana", "total"),
        ("max_unidades", "maximo", "unidades"),
        ("desv_estandar", "desviacion_estandar", "total"),
        ("registros", "contar", None),
    ])
    print(resumen.mostrar(max_filas=10))
    print()

    print("=" * 60)
    print("8. GUARDAR A CSV (salidas/resumen_ciudades_test.csv)")
    print("=" * 60)
    Path("salidas").mkdir(exist_ok=True)
    resumen.guardar_csv("salidas/resumen_ciudades_test.csv")
    print("Archivo guardado con exito. Verificando lectura del archivo creado:")
    leido = Tabla.cargar_csv("salidas/resumen_ciudades_test.csv")
    print(leido.mostrar(max_filas=5))
    print()

    print("=" * 60)
    print("TODAS LAS PRUEBAS DE LA CLASE TABLA PASARON EXITOSAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()
