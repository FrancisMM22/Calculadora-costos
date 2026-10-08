"""Análisis financiero del catálogo para la estrategia de precios.

El margen configurable se define como markup (ganancia / costo). Por eso
precio sugerido = costo total * (1 + markup / 100), mientras que el margen
neto mostrado se calcula sobre la venta: (precio - costo) / precio.

La base no guarda unidades vendidas ni una clave que vincule gastos generales
con productos. El prorrateo actual es una estimación por SKU activo; no debe
interpretarse como asignación contable ni como punto de equilibrio del negocio.
"""

from __future__ import annotations

import math
from statistics import median
from typing import Any

from services.calculadora import product_cost


def _estado(margen_venta: float, porcentaje_mp: float, costo_mp: float, mediana_mp: float) -> str:
    """Clasificación dinámica de conveniencia; la materia prima faltante es crítica."""
    if costo_mp <= 0 or margen_venta < 20 or porcentaje_mp >= 80:
        return "Crítico"
    if margen_venta >= 30 and costo_mp <= mediana_mp:
        return "Estrella"
    return "Estándar"


def analizar_catalogo(db: Any, margen_objetivo: float) -> list[dict[str, Any]]:
    """Calcula costo directo, prorrateo estimado, equilibrio y precio sugerido.

    No divide si el catálogo está vacío. Los importes y el markup se validan
    como finitos; la vista muestra el prorrateo y explica su supuesto.
    """
    markup = float(margen_objetivo)
    if not math.isfinite(markup) or markup < 0:
        raise ValueError("El recargo objetivo debe ser un número finito no negativo.")

    productos = db.list_products()
    if not productos:
        return []

    costos = db.list_general_costs(include_inactive=False)
    try:
        total_costos_generales = math.fsum(float(c["monto"]) for c in costos)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Hay costos generales con importes inválidos.") from exc
    if not math.isfinite(total_costos_generales) or total_costos_generales < 0:
        raise ValueError("Los costos generales deben ser finitos y no negativos.")

    # `productos` se comprobó arriba; evita división por cero y prorratea por SKU.
    prorrateo = total_costos_generales / len(productos)
    costos_mp = {
        p["id"]: product_cost(db.product_ingredients(p["id"]))
        for p in productos
    }
    mediana_mp = median(costos_mp.values()) if costos_mp else 0.0
    factor = markup / 100.0
    resultado: list[dict[str, Any]] = []

    for producto in productos:
        costo_mp = costos_mp[producto["id"]]
        costo_total = costo_mp + prorrateo
        # Precio de equilibrio unitario = costo total (ganancia cero).
        precio_equilibrio = costo_total
        # Fórmula elegida: markup sobre el costo, no margen sobre la venta.
        recomendado = costo_total * (1.0 + factor)
        if not all(math.isfinite(v) for v in (costo_total, recomendado)):
            raise ValueError(f"El costo calculado para '{producto['nombre']}' excede el rango válido.")
        ganancia = recomendado - costo_total
        margen_neto = (ganancia / recomendado * 100.0) if recomendado > 0 else 0.0
        porcentaje_mp = (costo_mp / costo_total * 100.0) if costo_total > 0 else 0.0
        resultado.append({
            "id": producto["id"], "nombre": producto["nombre"],
            "costo_mp": costo_mp, "prorrateo": prorrateo,
            "costo_total": costo_total, "precio_equilibrio": precio_equilibrio,
            "precio_recomendado": recomendado,
            "ganancia_estimada": ganancia, "margen_neto": margen_neto,
            "porcentaje_mp": porcentaje_mp,
            "estado": _estado(margen_neto, porcentaje_mp, costo_mp, mediana_mp),
            "mediana_mp": mediana_mp,
            "precio_actual": None,
        })
    return resultado


def actualizar_precio_actual(item: dict[str, Any], precio: float | None) -> dict[str, Any]:
    """Recalcula ganancia, margen de venta y estado para el precio observado."""
    actualizado = dict(item)
    actualizado["precio_actual"] = precio
    if precio is None:
        actualizado["ganancia_actual"] = item["ganancia_estimada"]
        actualizado["margen_actual"] = None
        actualizado["estado"] = _estado(
            item["margen_neto"], item["porcentaje_mp"], item["costo_mp"], item["mediana_mp"]
        )
        return actualizado

    precio = float(precio)
    if not math.isfinite(precio) or precio <= 0:
        raise ValueError("El precio actual debe ser un número finito mayor a cero.")
    ganancia = precio - float(item["costo_total"])
    margen = ganancia / precio * 100.0
    actualizado["ganancia_actual"] = ganancia
    actualizado["margen_actual"] = margen
    actualizado["estado"] = _estado(
        margen, item["porcentaje_mp"], item["costo_mp"], item["mediana_mp"]
    )
    return actualizado
