"""Cálculos de rentabilidad para el catálogo de productos."""

from __future__ import annotations

from statistics import median
from typing import Any

from services.calculadora import product_cost


def analizar_catalogo(db: Any, margen_objetivo: float) -> list[dict[str, Any]]:
    """Calcula costos y precios; el margen objetivo se interpreta como recargo."""
    productos = db.list_products()
    if not productos:
        return []

    # El esquema no vincula costos generales con unidades producidas. Se
    # distribuye el monto activo en partes iguales entre los productos activos.
    costos = db.list_general_costs(include_inactive=False)
    prorrateo = sum(float(c["monto"]) for c in costos) / len(productos)
    costos_mp = {
        p["id"]: product_cost(db.product_ingredients(p["id"]))
        for p in productos
    }
    mediana_mp = median(costos_mp.values()) if costos_mp else 0.0
    factor = max(0.0, float(margen_objetivo)) / 100
    resultado = []

    for producto in productos:
        costo_mp = costos_mp[producto["id"]]
        costo_total = costo_mp + prorrateo
        recomendado = costo_total * (1 + factor)
        actual = None
        ganancia = recomendado - costo_total
        margen_neto = (ganancia / recomendado * 100) if recomendado else 0.0
        porcentaje_mp = (costo_mp / costo_total * 100) if costo_total else 0.0
        if costo_mp <= 0 or margen_neto < 20 or porcentaje_mp >= 80:
            estado = "Crítico"
        elif margen_neto >= 30 and (mediana_mp == 0 or costo_mp <= mediana_mp):
            estado = "Estrella"
        else:
            estado = "Estándar"
        resultado.append({
            "id": producto["id"], "nombre": producto["nombre"],
            "costo_mp": costo_mp, "prorrateo": prorrateo,
            "costo_total": costo_total, "precio_recomendado": recomendado,
            "ganancia_estimada": ganancia, "margen_neto": margen_neto,
            "porcentaje_mp": porcentaje_mp, "estado": estado,
            "precio_actual": actual,
        })
    return resultado


def actualizar_precio_actual(item: dict[str, Any], precio: float | None) -> dict[str, Any]:
    """Actualiza las métricas de una fila con un precio ingresado por el usuario."""
    item = dict(item)
    item["precio_actual"] = precio
    ganancia = precio - item["costo_total"] if precio is not None else item["ganancia_estimada"]
    item["ganancia_actual"] = ganancia
    item["margen_actual"] = ganancia / precio * 100 if precio and precio > 0 else None
    return item
