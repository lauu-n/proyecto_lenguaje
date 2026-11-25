# COCOGRAFICAR (matplotlib)

import struct
import zlib
import os
import math
import unicodedata

FUENTE = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "_": (0, 0, 0, 0, 0, 0, 0x1F),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "^": (0x04, 0x0A, 0x11, 0, 0, 0, 0),
}

# Quita tildes y pasa a mayusculas porque la fuente bitmap solo tiene A-Z.
def _normalizar(texto):
    s = unicodedata.normalize("NFKD", str(texto)) #separa la e de su tilde é, y el filtro combining descarta la tilde. 
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.upper()

# Ancho en pixeles que ocupara un texto.
'''
cada letra mide 5 píxeles más 1 de espacio, o sea 6, por la escala. 
Restamos un espacio final porque después de la última letra no hace falta separación.
'''
def ancho_texto(texto, escala=2):
    n = len(_normalizar(texto))
    return max(0, n * 6 * escala - escala)

"""La función busca un paso redondo (1, 2, 2.5, 5 o 10 multiplicado por una potencia de 10):
Paso crudo: (50-12)/5 = 7.6.
Magnitud: log10(7.6) ≈ 0.88, y floor da 0, así que mag = 10**0 = 1. Es la potencia de 10 "más cercana por debajo".
Paso redondo: probamos 1, 2, 2.5, 5, 10 por mag, y nos quedamos con el primero que sea >= 7.6. Resulta 10.
Inicio y fin: ini = floor(12/10)*10 = 10 y fin = ceil(50/10)*10 = 50. El inicio se redondea hacia abajo y el fin hacia arriba, para que las marcas cubran todos los datos.
La lista: [10, 20, 30, 40, 50].
"""
def _ticks(lo, hi, n=6):
    """Marcas 'bonitas' para un eje que cubra [lo, hi]."""
    if hi == lo:
        hi = lo + 1
    paso = (hi - lo) / (n - 1)
    mag = 10 ** math.floor(math.log10(paso))
    for m in (1, 2, 2.5, 5, 10):
        if m * mag >= paso:
            paso = m * mag
            break
    ini = math.floor(lo / paso + 1e-9) * paso
    fin = math.ceil(hi / paso - 1e-9) * paso
    k = int(round((fin - ini) / paso))
    return [round(ini + i * paso, 10) for i in range(k + 1)]

"""
Un eje con 42000000 en cada marca no cabe en el margen. Esta función lo acorta a 42M, o 15000 a 15K. 
El formato :g quita los ceros sobrantes (2.0 queda 2, y 0.50 queda 0.5). Por eso el alfabeto de la fuente incluye K y M
"""
def _fmt(v):
    """Formato corto para numeros de los ejes."""
    a = abs(v)
    if a >= 1e6:
        return f"{v / 1e6:g}M"
    if a >= 1e4:
        return f"{v / 1e3:g}K"
    return f"{v:g}"

# BLOQUE 1 preparar los datos----------
def _num(valor, columna):
    """Valida que un valor sea numerico (y no booleano)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(
            f"Error semantico: la columna '{columna}' debe ser numerica "
            f"para este grafico (se encontro '{valor}')."
        )
    return valor


def _prep_barras(tabla, x, y):
    cats, vals = [], []
    for f in tabla.filas:
        if f.get(x) is None or f.get(y) is None:
            continue
        cats.append(str(f[x]))
        vals.append(_num(f[y], y))
    if not cats:
        raise ValueError("Error semantico: no hay datos validos para graficar.")

    def dibujar(L, fx, fy, color):
        mitad = 0.35 * (fx(1) - fx(0))
        for i, v in enumerate(vals):
            L.rect(fx(i) - mitad, fy(v), fx(i) + mitad, fy(0), color)
            L.contorno(fx(i) - mitad, fy(v), fx(i) + mitad, fy(0), (0, 0, 0))

    """
    Cada función _prep_* devuelve un diccionario. Ahora tendrá dos campos para el eje x:
    cats: lista de categorías, si el eje x es categórico (barras).
    xlim: tupla (mínimo, máximo), si el eje x es numérico.
    """
    return {"cats": cats, "xlim": None,
            "ylim": (min(0, min(vals)), max(0, max(vals))),
            "dibujar": dibujar}

"""
HISTOGRAMA
Recoge los datos de una sola columna, ignorando nulos
Cuántos rangos (bins): la regla de Sturges dice k = ceil(log2(n)) + 1. 
Con 15 datos: log2(15) ≈ 3.9, que redondea a 4, y +1 da 5 rangos. 
Es una regla clásica de estadística para elegir el número de barras sin pensarlo.
Ancho de cada rango: (máximo - mínimo) / k.
Contar: para cada dato, int((v - lo) / ancho) dice en qué rango cae. 
El min(..., k - 1) cubre un caso borde: el dato máximo da exactamente k, que se saldría de la lista, así que lo metemos en el último rango.
Dibujar: cada barra va de lo + i*ancho a lo + (i+1)*ancho en el eje x. Como esas posiciones son valores numéricos, se pasan por fx. 
Aquí las barras se tocan entre sí (no hay separación), que es lo que distingue a un histograma de una gráfica de barras.
"""
def _prep_histograma(tabla, x):
    datos = [_num(f[x], x) for f in tabla.filas if f.get(x) is not None]
    if not datos:
        raise ValueError(f"Error semantico: la columna '{x}' no tiene datos para el histograma.")
    lo, hi = min(datos), max(datos)
    if lo == hi:
        lo, hi = lo - 0.5, hi + 0.5
    k = max(1, math.ceil(math.log2(len(datos))) + 1)   # regla de Sturges
    ancho = (hi - lo) / k
    cuentas = [0] * k
    for v in datos:
        cuentas[min(int((v - lo) / ancho), k - 1)] += 1

    def dibujar(L, fx, fy, color):
        for i, c in enumerate(cuentas):
            xa, xb = fx(lo + i * ancho), fx(lo + (i + 1) * ancho)
            L.rect(xa, fy(c), xb, fy(0), color)
            L.contorno(xa, fy(c), xb, fy(0), (0, 0, 0))

    return {"cats": None, "xlim": (lo, hi), "ylim": (0, max(cuentas)), "dibujar": dibujar}


# Muestrear la curva. Valida el modelo antes de usarlo.
def _evaluar(modelo, x):
    """Evalua un modelo de ml.py en un punto x."""
    if not isinstance(modelo, dict) or "tipo" not in modelo:
        raise TypeError("Error semantico: 'ajuste' debe ser un modelo entrenado.")
    if modelo["tipo"] == "lineal":
        return modelo["m"] * x + modelo["b"]
    if modelo["tipo"] == "polinomial":
        return modelo["a"] * x * x + modelo["b"] * x + modelo["c"]
    raise ValueError(
        f"Error semantico: no se puede graficar un modelo '{modelo['tipo']}'; "
        f"solo 'lineal' y 'polinomial'."
    )

def _signo(v):
    return f"- {abs(v):g}" if v < 0 else f"+ {v:g}"

# evita que salga + -3
def _ecuacion(modelo):
    """Texto de la ecuacion, para mostrarlo en la leyenda."""
    if modelo["tipo"] == "lineal":
        return f"y = {modelo['m']:g}x {_signo(modelo['b'])}"
    return f"y = {modelo['a']:g}x^2 {_signo(modelo['b'])}x {_signo(modelo['c'])}"

def _recortar_recta(w1, w2, b, xa, xb, ya, yb): # calcula dónde corta el rectángulo del gráfico (4 intersecciones posibles, una por borde) y dibuja solo ese tramo.
    """Recorta la recta w1*x + w2*y + b = 0 al rectangulo [xa,xb] x [ya,yb]."""
    pts, eps = [], 1e-9
    if w2 != 0:
        for x in (xa, xb):                      # cortes con los bordes izq/der
            y = -(w1 * x + b) / w2
            if ya - eps <= y <= yb + eps:
                pts.append((x, y))
    if w1 != 0:
        for y in (ya, yb):                      # cortes con los bordes arriba/abajo
            x = -(w2 * y + b) / w1
            if xa - eps <= x <= xb + eps:
                pts.append((x, y))
    if len(pts) < 2:
        return None
    pts.sort()
    return pts[0], pts[-1]


"""
DISPERSiÓN
Cada fila es un punto (x, y), y se dibuja un círculo de radio 5 en (fx(x), fy(y)). 
Aquí los dos ejes son numéricos, y por eso se valida con _num tanto x como y.
Se muestrean puntos y se unen
ylim incluye la curva
"""
def _prep_dispersion(tabla, x, y, modelo=None, col_clase=None):
    filas = [f for f in tabla.filas
             if f.get(x) is not None and f.get(y) is not None
             and (col_clase is None or f.get(col_clase) is not None)]
    if not filas:
        raise ValueError("Error semantico: no hay datos validos para graficar.")
    pares = [(_num(f[x], x), _num(f[y], y), f[col_clase] if col_clase else None)
             for f in filas]
    xs, ys = [p[0] for p in pares], [p[1] for p in pares]
    lo, hi = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    es_perceptron = isinstance(modelo, dict) and modelo.get("tipo") == "perceptron"

    # Curva de regresion (lineal / polinomial)
    curva = []
    if modelo is not None and not es_perceptron:
        curva = [(lo + (hi - lo) * i / 100, _evaluar(modelo, lo + (hi - lo) * i / 100))
                 for i in range(101)]
        cy = [p[1] for p in curva]
        ymin, ymax = min(ymin, min(cy)), max(ymax, max(cy))

    # Margen del 10% para que los puntos no queden pegados al marco
    if col_clase is not None or es_perceptron:
        mx = (hi - lo) * 0.1 or 0.5
        my = (ymax - ymin) * 0.1 or 0.5
        lo, hi, ymin, ymax = lo - mx, hi + mx, ymin - my, ymax + my

    # Un color por clase
    clases = sorted({p[2] for p in pares}, key=str) if col_clase else []
    color_de = {c: COLORES_CLASE[i % len(COLORES_CLASE)] for i, c in enumerate(clases)}

    # Frontera de decision del perceptron
    recta = None
    if es_perceptron:
        pesos = modelo.get("pesos", [])
        if len(pesos) != 2:
            raise ValueError("Error semantico: solo se grafican perceptrones de 2 entradas.")
        recta = _recortar_recta(pesos[0], pesos[1], modelo["sesgo"], lo, hi, ymin, ymax)

    def dibujar(L, fx, fy, color):
        for vx, vy, c in pares:
            L.circulo(fx(vx), fy(vy), 6, color_de[c] if col_clase else color)
        for p, q in zip(curva, curva[1:]):
            L.linea(fx(p[0]), fy(p[1]), fx(q[0]), fy(q[1]), PALETA[1], grosor=3)
        if recta:
            (ax, ay), (bx, by) = recta
            L.linea(fx(ax), fy(ay), fx(bx), fy(by), (0, 0, 0), grosor=3)

    entradas = [(color_de[c], "cuadro", f"Clase {c}") for c in clases]
    if recta:
        entradas.append(((0, 0, 0), "linea", "Frontera de decision"))

    return {"cats": None, "xlim": (lo, hi), "ylim": (ymin, ymax), "dibujar": dibujar,
            "etiqueta_modelo": _ecuacion(modelo) if modelo is not None and not es_perceptron else None,
            "entradas_extra": entradas,
            "usa_clases": col_clase is not None,
            "leyenda_fuera": col_clase is not None or es_perceptron}

"""
LÍNEAS
Una gráfica de líneas es una dispersión con los puntos unidos en orden. El eje x puede ser de dos clases:
Numérico (por ejemplo, unidades): se ordenan los puntos por x y se usa la regla de tres del paso 4.
Texto o fechas (por ejemplo, "2026-01-05"): se tratan como categorías, igual que en barras, en el orden en que aparecen.
"""
def _prep_lineas(tabla, x, y):
    pares = [(f[x], _num(f[y], y)) for f in tabla.filas
             if f.get(x) is not None and f.get(y) is not None]
    if not pares:
        raise ValueError("Error semantico: no hay datos validos para graficar.")
    numerico = all(isinstance(p[0], (int, float)) and not isinstance(p[0], bool) # Decide la clase de eje x: numerico es verdadero solo si todos los x son números.
                   for p in pares)
    ys = [p[1] for p in pares]

    def trazar(L, puntos, color): 
        for a, b in zip(puntos, puntos[1:]): # zip(puntos, puntos[1:]) forma parejas de puntos vecinos: (1º, 2º), (2º, 3º), y así.
            L.linea(a[0], a[1], b[0], b[1], color, grosor=2)
        for px, py in puntos:
            L.circulo(px, py, 3, color)

    if numerico:
        pares.sort(key=lambda p: p[0]) # pares.sort(key=lambda p: p[0]) ordena por x. Sin esto, si los datos vienen desordenados
        xs = [p[0] for p in pares]

        def dibujar(L, fx, fy, color):
            trazar(L, [(fx(a), fy(b)) for a, b in pares], color)

        return {"cats": None, "xlim": (min(xs), max(xs)),
                "ylim": (min(ys), max(ys)), "dibujar": dibujar}

    cats = [str(p[0]) for p in pares]

    def dibujar(L, fx, fy, color):
        trazar(L, [(fx(i), fy(b)) for i, (_, b) in enumerate(pares)], color)

    return {"cats": cats, "xlim": None, "ylim": (min(ys), max(ys)), "dibujar": dibujar}



# BLOQUE 2 layout y escalas----------

ANCHO, ALTO = 800, 500
MARGEN_IZQ, MARGEN_DER, MARGEN_SUP = 100, 30, 55
PALETA = [(182, 149, 192), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189)]
COLORES_CLASE = [PALETA[0], PALETA[3], PALETA[2], PALETA[4]]

TIPOS = ("barras", "lineas", "histograma", "dispersion")

def graficar(tipo, tabla, x, y=None, titulo=None, etiqueta_x=None,
             etiqueta_y=None, leyenda=None, ruta=None, modelo=None, col_clase=None):
    """Dibuja una grafica a partir de una Tabla y la guarda como PNG."""
    if tipo not in TIPOS:                                         # NUEVO
        raise ValueError(f"Tipo de grafico desconocido: '{tipo}'. Validos: {TIPOS}")

    tabla._validar_columnas([x] + ([y] if y else []) + ([col_clase] if col_clase else []))
    if tipo != "histograma" and y is None:                        # NUEVO
        raise ValueError(f"Error semantico: el grafico '{tipo}' requiere un eje y.")
    if modelo is not None and tipo != "dispersion":
        raise ValueError("Error semantico: 'ajuste' solo se puede usar con graficos de dispersion.")
    if col_clase is not None and tipo != "dispersion":
        raise ValueError("Error semantico: 'por_clase' solo se puede usar con graficos de dispersion.")

    preparadores = {                                              # NUEVO
        "barras": lambda: _prep_barras(tabla, x, y),
        "lineas": lambda: _prep_lineas(tabla, x, y),
        "histograma": lambda: _prep_histograma(tabla, x),
        "dispersion": lambda: _prep_dispersion(tabla, x, y, modelo, col_clase),
    }

    prep = preparadores[tipo]()

    cats = prep["cats"]
    yt = _ticks(*prep["ylim"])
    ylo, yhi = yt[0], yt[-1]
    if cats is None:                                              # NUEVO
        xt = _ticks(*prep["xlim"])
        xlo, xhi = xt[0], xt[-1]

    ancho_plot = ANCHO - MARGEN_IZQ - MARGEN_DER
    rotar, maxw, etiquetas = False, 14, []                        # NUEVO
    if cats is not None:
        etiquetas = [c if len(c) <= 10 else c[:9] + "." for c in cats]
        maxw = max(ancho_texto(e) for e in etiquetas)
        rotar = maxw > ancho_plot / len(cats) - 6
    margen_inf = 60 + (maxw if rotar else 14)

    # Leyenda
    entradas = []
    if leyenda and not prep.get("usa_clases"):
        entradas.append((PALETA[0], "cuadro", leyenda))
    if prep.get("etiqueta_modelo"):
        entradas.append((PALETA[1], "linea", prep["etiqueta_modelo"]))
    entradas += prep.get("entradas_extra", [])

    w_ley = max((ancho_texto(t) for _, _, t in entradas), default=0) + 40
    fuera = bool(entradas) and prep.get("leyenda_fuera", False)
    margen_der = w_ley + 25 if fuera else MARGEN_DER

    # Área de dibujo
    ancho_plot = ANCHO - MARGEN_IZQ - margen_der

    px0 = MARGEN_IZQ
    px1 = ANCHO - margen_der
    py0 = MARGEN_SUP
    py1 = ALTO - margen_inf
    def fx(v):
        if cats is not None:                                      # NUEVO
            return px0 + (v + 0.5) * ancho_plot / len(cats)
        return px0 + (v - xlo) / (xhi - xlo) * ancho_plot

    def fy(v):
        return py1 - (v - ylo) / (yhi - ylo) * (py1 - py0)

    L = Lienzo(ANCHO, ALTO)
    color = PALETA[0]

    # Cuadricula
    for t in yt:
        L.linea(px0, fy(t), px1, fy(t), (225, 225, 225))
    if cats is None:                                              # NUEVO
        for t in xt:
            L.linea(fx(t), py0, fx(t), py1, (225, 225, 225))

    # Datos
    prep["dibujar"](L, fx, fy, color)

    # Marco y marcas del eje y
    L.contorno(px0, py0, px1, py1, (0, 0, 0), grosor=2)
    for t in yt:
        L.linea(px0 - 5, fy(t), px0, fy(t), (0, 0, 0))
        txt = _fmt(t)
        L.texto(px0 - 10 - ancho_texto(txt), fy(t) - 7, txt)

    # Marcas del eje x
    if cats is None:                                              # NUEVO
        for t in xt:
            L.linea(fx(t), py1, fx(t), py1 + 5, (0, 0, 0))
            txt = _fmt(t)
            L.texto(fx(t) - ancho_texto(txt) // 2, py1 + 10, txt)
    else:
        for i, e in enumerate(etiquetas):
            L.linea(fx(i), py1, fx(i), py1 + 5, (0, 0, 0))
            if rotar:
                L.texto_vertical(fx(i) - 7, py1 + 10 + ancho_texto(e), e)
            else:
                L.texto(fx(i) - ancho_texto(e) // 2, py1 + 10, e)

    # Titulo, etiquetas de ejes y leyenda (igual que antes)
    if titulo:
        L.texto((ANCHO - ancho_texto(titulo, 3)) // 2, 15, titulo, escala=3)

    et_x = etiqueta_x or x
    L.texto(px0 + (ancho_plot - ancho_texto(et_x)) // 2, ALTO - 28, et_x)

    et_y = etiqueta_y or (y if y else "frecuencia")               # NUEVO
    L.texto_vertical(15, (py0 + py1) // 2 + ancho_texto(et_y) // 2, et_y)
    
    if entradas:
        w = w_ley
        alto = 24 * len(entradas) + 4
        lx, ly = (px1 + 12, py0) if fuera else (px1 - w - 10, py0 + 10)
        L.rect(lx, ly, lx + w, ly + alto, (255, 255, 255))
        L.contorno(lx, ly, lx + w, ly + alto, (120, 120, 120))
        for i, (c, forma, t) in enumerate(entradas):
            ry = ly + 5 + 24 * i
            if forma == "cuadro":
                L.rect(lx + 8, ry + 1, lx + 22, ry + 15, c)
            else:
                L.linea(lx + 8, ry + 8, lx + 22, ry + 8, c, grosor=3)
            L.texto(lx + 30, ry + 1, t)

    # Salida
    if ruta:
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        L.guardar_png(ruta)
        return f"Grafico guardado en '{ruta}'"
    raise ValueError("Falta 'guardar como': la ventana de vista previa se agrega despues.")




class Lienzo:
    # Un lienzo es un arreglo de pixeles RGB, cada pixel ocupa 3 bytes (R, G, B)
    # Constructor: la imagen en memoria
    def __init__(self, ancho, alto, fondo=(255, 255, 255)):
        self.ancho = ancho
        self.alto = alto
        # bytes(fondo) -> 3 bytes (R, G, B); se repite por cada pixel
        self.datos = bytearray(bytes(fondo) * (ancho * alto))


    # Rectangulo relleno (coordenadas, recortado al lienzo).
    def rect(self, x0, y0, x1, y1, color):
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        x0, y0 = max(x0, 0), max(y0, 0) # recortan el rectángulo a los bordes de la imagen
        x1, y1 = min(x1, self.ancho - 1), min(y1, self.alto - 1) #recortan el rectángulo a los bordes de la imagen
        if x0 > x1 or y0 > y1:
            return
        fila = bytes(color) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            i = (y * self.ancho + x0) * 3
            self.datos[i:i + len(fila)] = fila

    # Rectangulo contorno (coordenadas, recortado al lienzo).
    def contorno(self, x0, y0, x1, y1, color, grosor=1):
        """Borde de un rectangulo."""
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        g = grosor - 1
        self.rect(x0, y0, x1, y0 + g, color)   # lado de arriba
        self.rect(x0, y1 - g, x1, y1, color)   # lado de abajo
        self.rect(x0, y0, x0 + g, y1, color)   # lado izquierdo
        self.rect(x1 - g, y0, x1, y1, color)   # lado derecho

    # Circulo relleno (coordenadas, recortado al lienzo).
    def circulo(self, cx, cy, r, color):
        cx, cy, r = int(round(cx)), int(round(cy)), int(r)
        for dy in range(-r, r + 1):
            w = int(math.sqrt(r * r - dy * dy))
            self.rect(cx - w, cy + dy, cx + w, cy + dy, color)

    # Linea (coordenadas, recortado al lienzo).
    def linea(self, x0, y0, x1, y1, color, grosor=1):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - grosor // 2, y0 - grosor // 2, x0 + grosor // 2, y0 + grosor // 2, color)
            if x0 == x1 and y0 == y1:
                break
            err2 = err * 2
            if err2 > -dy:
                err -= dy
                x0 += sx
            if err2 < dx:
                err += dx
                y0 += sy

    # Guardar la imagen en un archivo PNG. 
    def guardar_png(self, ruta):
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

        def chunk(tipo, datos):
            cuerpo = tipo + datos
            return (struct.pack(">I", len(datos)) + cuerpo
                    + struct.pack(">I", zlib.crc32(cuerpo) & 0xFFFFFFFF))

        paso = self.ancho * 3  # bytes por fila

        crudo = b"".join(
            b"\x00" + bytes(self.datos[y * paso:(y + 1) * paso])
            for y in range(self.alto)
        )
        png = (
            b"\x89PNG\r\n\x1a\n"  # firma de todo PNG
            + chunk(b"IHDR", struct.pack(">IIBBBBB", self.ancho, self.alto, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(crudo))
            + chunk(b"IEND", b"")
        )

        with open(ruta, "wb") as archivo:
            archivo.write(png)

    '''
        En Python, "wb" es un modo de apertura de archivos. Se compone de dos letras:
        w (write): significa escribir. Abre un archivo para escribir información. Si ya existe, reemplaza su contenido.
        b (binary): significa binario. Indica que vamos a escribir datos en formato binario, no texto.
    '''    

    # Dibujar texto en el lienzo. (x, y) es la esquina superior izquierda del primer carácter
    '''
    Por cada carácter busca su matriz en FUENTE (o "?" si no existe).
    f recorre las 7 filas y c las 5 columnas.
    El truco de bits: fila & (1 << (4 - c)) pregunta “¿está encendido el bit número c de esta fila?”. 1 << 4 es 10000, 1 << 3 es 01000, etc. Es una máscara que va revisando bit por bit de izquierda a derecha. Si el resultado no es cero, ese píxel es parte de la letra.
    Cada píxel de la letra se pinta como un cuadrito de escala x escala con rect. Con escala=1 la letra mide 5x7 píxeles (diminuta), con escala=2 mide 10x14, y con escala=3 mide 15x21.
    cx += 6 * escala mueve el cursor a la siguiente letra.
    '''
    def texto(self, x, y, texto, color=(0, 0, 0), escala=2):
        """Texto horizontal; (x, y) es la esquina superior izquierda."""
        cx = int(x)
        for ch in _normalizar(texto):
            glifo = FUENTE.get(ch, FUENTE["?"])
            for f, fila in enumerate(glifo):
                for c in range(5):
                    if fila & (1 << (4 - c)):
                        px = cx + c * escala
                        py = int(y) + f * escala
                        self.rect(px, py, px + escala - 1, py + escala - 1, color)
            cx += 6 * escala

    def texto_vertical(self, x, y, texto, color=(0, 0, 0), escala=2):
        """Texto rotado 90 grados (se lee de abajo hacia arriba).
        (x, y) es la esquina inferior izquierda donde empieza el texto.
        """
        pos = 0
        for ch in _normalizar(texto):
            glifo = FUENTE.get(ch, FUENTE["?"])
            for f, fila in enumerate(glifo):
                for c in range(5):
                    if fila & (1 << (4 - c)):
                        px = int(x) + f * escala
                        py = int(y) - (pos + c * escala)

                        self.rect(
                            px,
                            py - escala + 1,
                            px + escala - 1,
                            py,
                            color
                        )
            pos += 6 * escala

#------------------------------


ANCHO, ALTO = 800, 500
px0, px1, py0, py1 = 100, 770, 55, 430   # area de la grafica

xs = [1, 2, 3, 4, 5]
ys = [12, 35, 28, 50, 41]

yt = _ticks(min(ys), max(ys))
xt = _ticks(min(xs), max(xs))
ylo, yhi = yt[0], yt[-1]
xlo, xhi = xt[0], xt[-1]

"""
de dato a píxel
Es una regla de tres. Primero calculas qué fracción del recorrido es el valor, y luego avanzas esa fracción por la altura:
(v - ylo) / (yhi - ylo) da un número entre 0 y 1 (0 es el mínimo, 1 es el máximo). Para v=30: (30-10)/(50-10) = 0.5.
* (py1 - py0) lo convierte en una cantidad de píxeles: 0.5 * 375 = 187.5.
py1 - ... resta desde abajo, porque en una imagen la y crece hacia abajo (el píxel 0 es el techo). En una gráfica queremos que los valores grandes suban, así que hay que invertir.
"""
def fy(v):
    return py1 - (v - ylo) / (yhi - ylo) * (py1 - py0)

"""
Para el eje x es lo mismo, pero sin invertir
Interpolación lineal
"""
def fx(v):
    return px0 + (v - xlo) / (xhi - xlo) * (px1 - px0)

    

'''
        paso es cuántos bytes tiene una fila (200 píxeles x 3 = 600).
        Para cada fila y, se corta su pedazo de la cinta con datos[y*paso : (y+1)*paso].
        Se le pone un byte \x00 al principio. En PNG, cada fila empieza con un byte que indica el “filtro” aplicado, y 0 significa “ninguno”. Si lo olvidas, el PNG sale corrupto.
        b"".join(...) pega todas las filas en un solo bloque de bytes.
'''
# ---------------
# PRUEBAS
# ----------------

L = Lienzo(ANCHO, ALTO)

'''
1. Para pintar un píxel rojo en la mitad (x=100, y=50):
    y * ancho salta las 50 filas anteriores (cada una de 200 píxeles).
    + x avanza 100 píxeles dentro de la fila.
    * 3 convierte “número de píxel” en “número de byte”, porque cada píxel ocupa 3 bytes.

i = (50 * 200 + 100) * 3          # posicion del pixel (x=100, y=50)
L.datos[i:i + 3] = bytes((255, 0, 0))
L.guardar_png("salidas/prueba1.png")
print("Listo: abre salidas/prueba1.png")
'''

# Cuadricula
for t in yt:
    L.linea(px0, fy(t), px1, fy(t), (225, 225, 225))
for t in xt:
    L.linea(fx(t), py0, fx(t), py1, (225, 225, 225))

# Datos: una linea con puntos
puntos = [(fx(a), fy(b)) for a, b in zip(xs, ys)]
for p, q in zip(puntos, puntos[1:]):
    L.linea(p[0], p[1], q[0], q[1], (182, 149, 192), grosor=2)
for px, py in puntos:
    L.circulo(px, py, 4, (182, 149, 192))

# Marco
L.contorno(px0, py0, px1, py1, (0, 0, 0), grosor=2)

# Marcas y numeros del eje y
for t in yt:
    L.linea(px0 - 5, fy(t), px0, fy(t), (0, 0, 0))
    txt = _fmt(t)
    L.texto(px0 - 10 - ancho_texto(txt), fy(t) - 7, txt)

# Marcas y numeros del eje x
for t in xt:
    L.linea(fx(t), py1, fx(t), py1 + 5, (0, 0, 0))
    txt = _fmt(t)
    L.texto(fx(t) - ancho_texto(txt) // 2, py1 + 10, txt)

print("Marcas y:", yt)
print("Marcas x:", xt)
