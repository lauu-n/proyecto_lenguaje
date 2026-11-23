"""Motor matematico de Machine Learning para Cocosette (Corte III).

Implementado en Python puro, sin bibliotecas externas (sin numpy ni scikit-learn).
Basado en los fundamentos teoricos de:
- Luis Serrano: 'Grokking Machine Learning' (The Square Trick, The Perceptron Trick).
- Rishal Hurbans: 'Grokking AI Algorithms' (Redes Neuronales y Perceptron).
"""

import math
from typing import Any, Dict, List, Tuple


# ====================================================================
# 1. REGRESION LINEAL (The Square Trick - Luis Serrano Cap. 3)
# ====================================================================

def entrenar_regresion_lineal(
    x_vals: List[float],
    y_vals: List[float],
    tasa: float = 0.01,
    epocas: int = 1000
) -> Dict[str, Any]:
    """Entrena un modelo de regresion lineal: y = m * x + b.

    Aplica el algoritmo 'The Square Trick' de Luis Serrano:
    Para cada punto (x, y):
      y_pred = m * x + b
      error = y - y_pred
      m += tasa * x * error
      b += tasa * error
    """
    n = len(x_vals)
    if n == 0 or len(y_vals) != n:
        return {"tipo": "lineal", "m": 0.0, "b": 0.0}

    m = 0.0
    b = 0.0

    for _ in range(int(epocas)):
        for x, y in zip(x_vals, y_vals):
            y_pred = m * x + b
            error = y - y_pred
            m += tasa * x * error
            b += tasa * error

    # Si por escala de datos hubo divergencia numerica, usamos la solucion analitica cerrada
    if math.isnan(m) or math.isinf(m) or math.isnan(b) or math.isinf(b):
        media_x = sum(x_vals) / n
        media_y = sum(y_vals) / n
        num = sum((x - media_x) * (y - media_y) for x, y in zip(x_vals, y_vals))
        den = sum((x - media_x) ** 2 for x in x_vals)
        m = num / den if den != 0 else 0.0
        b = media_y - m * media_x

    return {
        "tipo": "lineal",
        "m": round(m, 2),
        "b": round(b, 2)
    }


# ====================================================================
# 2. REGRESION POLINOMIAL (Curva Parabolica - Luis Serrano Cap. 4)
# ====================================================================

def _resolver_sistema_3x3(A: List[List[float]], b: List[float]) -> Tuple[float, float, float]:
    """Resuelve un sistema de 3 ecuaciones con 3 incognitas usando la regla de Cramer."""
    def det3(m):
        return (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )

    d_total = det3(A)
    if abs(d_total) < 1e-12:
        return 0.0, 0.0, 0.0

    A0 = [[b[0], A[0][1], A[0][2]], [b[1], A[1][1], A[1][2]], [b[2], A[2][1], A[2][2]]]
    A1 = [[A[0][0], b[0], A[0][2]], [A[1][0], b[1], A[1][2]], [A[2][0], b[2], A[2][2]]]
    A2 = [[A[0][0], A[0][1], b[0]], [A[1][0], A[1][1], b[1]], [A[2][0], A[2][1], b[2]]]

    return det3(A0) / d_total, det3(A1) / d_total, det3(A2) / d_total


def entrenar_regresion_polinomial(
    x_vals: List[float],
    y_vals: List[float]
) -> Dict[str, Any]:
    """Ajusta un polinomio de segundo grado: y = a * x^2 + b * x + c.

    Aplica las ecuaciones normales del metodo de minimos cuadrados para grado 2.
    """
    n = len(x_vals)
    if n < 3 or len(y_vals) != n:
        return {"tipo": "polinomial", "a": 0.0, "b": 0.0, "c": 0.0}

    s0 = float(n)
    s1 = sum(x_vals)
    s2 = sum(x**2 for x in x_vals)
    s3 = sum(x**3 for x in x_vals)
    s4 = sum(x**4 for x in x_vals)

    sy = sum(y_vals)
    sxy = sum(x * y for x, y in zip(x_vals, y_vals))
    sx2y = sum((x**2) * y for x, y in zip(x_vals, y_vals))

    A = [
        [s4, s3, s2],
        [s3, s2, s1],
        [s2, s1, s0]
    ]
    b_vec = [sx2y, sxy, sy]

    a, b, c = _resolver_sistema_3x3(A, b_vec)
    return {
        "tipo": "polinomial",
        "a": round(a, 2),
        "b": round(b, 2),
        "c": round(c, 2)
    }


# ====================================================================
# 3. PERCEPTRON Y REDES NEURONALES (Serrano Cap. 8, Hurbans Cap. 8)
# ====================================================================

def entrenar_perceptron(
    x1_vals: List[float],
    x2_vals: List[float],
    y_vals: List[float],
    tasa: float = 0.1,
    epocas: int = 1000
) -> Dict[str, Any]:
    """Entrena un Perceptron de 2 entradas con el algoritmo de clasificacion lineal.

    Paso de activacion (escalon unitario):
      y_pred = 1 si w1*x1 + w2*x2 + b >= 0 sino 0
    Actualizacion:
      w1 += tasa * (y - y_pred) * x1
      w2 += tasa * (y - y_pred) * x2
      b  += tasa * (y - y_pred)
    """
    w1, w2, b = 0.0, 0.0, -0.05
    for _ in range(int(epocas)):
        errores = 0
        for x1, x2, y in zip(x1_vals, x2_vals, y_vals):
            z = w1 * x1 + w2 * x2 + b
            pred = 1 if z >= 0 else 0
            err = y - pred
            if err != 0:
                w1 += tasa * err * x1
                w2 += tasa * err * x2
                b += tasa * err
                errores += 1
        if errores == 0:
            break

    return {
        "tipo": "perceptron",
        "pesos": [round(w1, 4), round(w2, 4)],
        "sesgo": round(b, 4)
    }


def crear_perceptron_manual(w1: float, w2: float, b: float) -> Dict[str, Any]:
    """Crea una neurona artificial directamente con pesos y sesgo predefinidos.

    Util para compuertas logicas (AND, OR, NAND) y construccion de
    Perceptrones Multicapa (MLP) para problemas no linealmente separables como XOR.
    """
    return {
        "tipo": "perceptron",
        "pesos": [round(float(w1), 4), round(float(w2), 4)],
        "sesgo": round(float(b), 4)
    }
